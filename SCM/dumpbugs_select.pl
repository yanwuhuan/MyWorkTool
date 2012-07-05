#!/usr/bin/perl
# --*-- encoding:utf-8 --*--

use strict;

#use utf8;
use Encode;
use File::Temp qw/ :POSIX /;
use Spreadsheet::WriteExcel::Big; # big Excel

use DBI;
use Encode;

use Archive::Zip qw( :ERROR_CODES :CONSTANTS );

#use HTTP::Request::Common;
#use LWP::UserAgent;

use MIME::Base64;
use MIME::Lite;
use Net::SMTP;


sub send_mail
{
    my ($from, $subject, $toref, $ccref, $body, $attach_path) = @_;
    my $user = 'gzitadmin';
    my $pass = 'gozone';

    my $host    = 'smtp.163.com';
    my $smtp    = Net::SMTP->new($host);#,   Debug   => 1);
    die "Could not open connection: $!" if (! defined $smtp);
    $smtp->auth($user, $pass);

    my @arr_to = ();
    my @arr_cc = ();

    if (defined $toref)
    {
        push @arr_to, $_ foreach (@$toref);
    }
    if (defined $ccref)
    {
        push @arr_cc, $_ foreach (@$ccref);
    }

    die "No To list" if $#arr_to == -1;
    my $str_to = join(",", @arr_to);
    my $str_cc = "";
    $str_cc = join(",", @arr_cc) if $#arr_cc != -1;
    print "str_to: $str_to\n";
    print "str_cc: $str_cc\n";


    my $subject_final = "=?utf-8?B?".encode_base64($subject,'')."?=";
    my $msg = MIME::Lite->new(
        From => $from,
        'Reply-To' => $from,
        To => $str_to,
        Cc => $str_cc,
        Subject => $subject_final,
        Type => "multipart/mixed"
        );
    my $part = MIME::Lite->new(
        Type => "text/html",
        Data => $body
        );
    $part->attr('content-type.charset' => 'UTF-8');
    $part->add('X-Comment' => 'content');

    $msg->attach($part);
        
    if (defined $attach_path)
    {
        $msg->attach(
            Type => "application/zip",
            Path => $attach_path,
            Filename => "dumpbugs.zip"
            );
    }

    my $cnt_string = $msg->as_string() or die "$!";

    $smtp->mail($from);
    #$smtp->to($str_to);
    $smtp->to($_) foreach @arr_to;
    #$smtp->cc($str_cc);
    $smtp->cc($_) foreach @arr_cc;
    $smtp->data();
    #smtp->datasend("Content-Type:text/html;charset=utf-8\n");
    #smtp->datasend("Content-Transfer-Encoding:base64\n");
    #smtp->datasend("From: gzitadmin\@163.com\n");
    #y $to = "To: ";
    #f (defined $toref)
    #
    #   $to = "$to$_," foreach (@$toref);
    #   $to = substr($to, 0, length($to)-1);
    #   $smtp->datasend("$to\n");
    #
    #y $cc = "Cc: ";
    #f (defined $ccref)
    #
    #   $cc = "$cc$_," foreach (@$ccref);
    #   $cc = substr($cc, 0, length($cc)-1);
    #   $smtp->datasend("$cc\n");
    #
    #
    #smtp->datasend("Subject:=?utf-8?B?".encode_base64($subject,'')."?=\n\n");
    #smtp->datasend("\n");
    #
    #smtp->datasend(encode_base64($body,'')." \n\n");

    $smtp->datasend($cnt_string);

    $smtp->dataend(); # Note, end, not send

    $smtp->quit();
    print "Notice emails sent!\n";
}


my $dbh = DBI->connect("DBI:mysql:database=bugs;host=localhost",
               "bugs", "V38VwsMenf6LExHq",
                       {'RaiseError' => 0});
$dbh->do("SET NAMES utf8");

my $product_id = 19;

# prepare for workboot
my $fname= tmpnam();
$fname = $fname . ".xls";
#$fname = "test.xls";
my $fname_zip = $fname . ".zip";


# Create new Excel
my $book_dump = Spreadsheet::WriteExcel::Big->new($fname) or die ("Create Execl error: $fname!");

# Add a work sheet
my $sheet_bugs = $book_dump->add_worksheet("Bugs"); 
$sheet_bugs->freeze_panes(1, 0); 

# Create a new format
my $format_title = $book_dump->addformat();
$format_title->set_bold();
$format_title->set_color("Blue");
$format_title->set_font("Times New Roman");
$format_title->set_size(12);
$format_title->set_align('left');

my $format_data = $book_dump->addformat();
$format_data->set_color("Black");
$format_data->set_font("Times New Roman");
$format_data->set_size(10);
$format_data->set_align('left');

my $format_long = $book_dump->addformat();
$format_long->set_color("Black");
$format_long->set_font("Times New Roman");
$format_long->set_size(10);
$format_long->set_align('left');
$format_long->set_text_wrap();

my $sth = $dbh->prepare("SELECT bugs.bug_id as bugid,bug_when,thetext FROM bugs,longdescs WHERE longdescs.bug_id=bugs.bug_id AND product_id=$product_id ORDER BY bugs.bug_id,comment_id;");
$sth->execute();

my %all_long;
while(my $ref = $sth->fetchrow_hashref())
{
    if (exists $all_long{$ref->{'bugid'}})
    {
        $all_long{$ref->{'bugid'}} = "$all_long{$ref->{'bugid'}}\n\n--- $ref->{'bug_when'} ---\n$ref->{'thetext'}";
    }
    else
    {
        $all_long{$ref->{'bugid'}} = "\'--- $ref->{'bug_when'} ---\n$ref->{'thetext'}";
    }
}

$sth->finish;


# pickup the userid <-> realname
my $sth = $dbh->prepare("SELECT userid,realname FROM profiles");
$sth->execute();

my %all_profiles;
while(my $ref = $sth->fetchrow_hashref())
{
    $all_profiles{$ref->{'userid'}} = $ref->{'realname'};
}

$sth->finish;

# dump bugs for products
# bug summary

my $sql = <<END_OF_SQL
SELECT
	bug_id,
	assigned_to,
	bug_severity,
	bug_status,
	creation_ts,
	delta_ts,
	short_desc,
	priority,
	cf_frequence,
	cf_mainver,
	cf_bug_company,
	products.name AS nameofprod,
	components.name AS nameofcomp,
	reporter
FROM
	bugs,
	products,
	components
WHERE
	bugs.product_id=$product_id
	AND products.id=bugs.product_id
	AND components.id=bugs.component_id
	AND bug_severity in ('1-critical','2-major','3-normal','4-minor','5-enhancement')
    AND components.name in ('1-SPDM','2-APP')
END_OF_SQL
    ;

my $sth = $dbh->prepare($sql);
$sth->execute();

my @summary         = qw /ID    Severity    Priority    Company Status  Freq  Module  Title   Comments    Created Changed Version Product Component/;
my @summary_widths  = qw /5  6  5   8   8  8 12 40   60   15  15  15 15 15/;
my $cnt = 0;
while ($cnt < @summary)
{
    $sheet_bugs->write(0, $cnt,  $summary[$cnt], $format_title); 
    $sheet_bugs->set_column($cnt, $cnt, $summary_widths[$cnt]);
    $cnt++;
}

my $row = 1;
my $col = 0;
while(my $ref = $sth->fetchrow_hashref())
{
    $col = 0;
    $sheet_bugs->write_number($row, $col, $ref->{'bug_id'}, $format_data);
    $col ++;

    #$sheet_bugs->write_unicode($row, $col, Encode::encode('ucs2',Encode::decode_utf8($all_profiles{$ref->{'assigned_to'}})), $format_data);
    #$col ++;

    $sheet_bugs->write_string($row, $col, $ref->{'bug_severity'}, $format_data);
    $col ++;

    $sheet_bugs->write_string($row, $col, $ref->{'priority'}, $format_data);
    $col ++;

    my $company = $ref->{'cf_bug_company'};
    $company = '1-Our Own' if ($company eq '---');
    $sheet_bugs->write_string($row, $col, $company, $format_data);
    $col ++;

    $sheet_bugs->write_string($row, $col, $ref->{'bug_status'}, $format_data);
    $col ++;

    $sheet_bugs->write_string($row, $col, $ref->{'cf_frequence'}, $format_data);
    $col ++;

    my $title = $ref->{'short_desc'};
    if ($title =~ /^\s*\[(.+?)\]/)
    {
        my $module = $1;
        $sheet_bugs->write_unicode($row, $col, Encode::encode('ucs2', Encode::decode_utf8($module)), $format_long);
    }
    $col ++;


    $sheet_bugs->write_unicode($row, $col, Encode::encode('ucs2', Encode::decode_utf8($ref->{'short_desc'})), $format_long);
    $col ++;

    $sheet_bugs->set_row($row, 50);
    $sheet_bugs->write_unicode($row, $col, Encode::encode('ucs2', Encode::decode_utf8($all_long{$ref->{'bug_id'}})), $format_long);
    $col ++;

    $sheet_bugs->write_date_time($row, $col, $ref->{'creation_ts'}, $format_data);
    $col ++;

    $sheet_bugs->write_date_time($row, $col, $ref->{'delta_ts'}, $format_data);
    $col ++;

    $sheet_bugs->write_unicode($row, $col, Encode::encode('ucs2', Encode::decode_utf8($ref->{'cf_mainver'})), $format_data);
    $col ++;

    $sheet_bugs->write_unicode($row, $col, Encode::encode('ucs2', Encode::decode_utf8($ref->{'nameofprod'})), $format_data);
    $col ++;

    $sheet_bugs->write_unicode($row, $col, Encode::encode('ucs2', Encode::decode_utf8($ref->{'nameofcomp'})), $format_data);
    $col ++;


    #$sheet_bugs->write_unicode($row, $col, Encode::encode('ucs2', Encode::decode_utf8($all_profiles{$ref->{'reporter'}})), $format_data);
    #$col ++;

    $row ++;
}

$sth->finish;


# --- end of sth ---
$book_dump->close;
$dbh->disconnect;

my $zipper = Archive::Zip->new();
$zipper->addFile($fname, "dumpbugs.xls");

if ($zipper->writeToFileNamed($fname_zip) != AZ_OK) 
{
    print "Error in archive creation!";
}
else
{
    my $tmp =  substr($fname_zip, 5);
    print "生成完毕: ", $fname_zip, "\n";
}

# remove the xls file
unlink $fname;


my (undef,undef,undef,$day,$mon,$year)=localtime(time());
$year += 1900;
$mon += 1;

my @tolist = ('');
my @cclist = ();
my $title = "UP812B项目测试日报 $year.$mon.$day";
my $body = "Hi,<br /><br />&nbsp;&nbsp;UP812B项目bug日报，请查收。";
send_mail('gzitadmin@163.com', $title, \@tolist, \@cclist, $body, $fname_zip);

# remove the archive zip file after send email
unlink $fname_zip;
