#!/usr/bin/perl

use strict;
use Getopt::Long;

$| = 1;

my $PATTERN;
my $_2013;
my $ANNOT = 0;

GetOptions(
    "p|pattern=s" => \$PATTERN,
    "2013" => \$_2013,
    "a|annotator=i" => \$ANNOT,
);

if ($_2013 and $PATTERN) {
    die "Do not specify '--2013' and '--pattern arg' at the same time!";
}

if ($PATTERN) {
    $PATTERN = "^($PATTERN)\$";
}

if ($_2013) {
    $PATTERN = "^(ArtOrDet|Nn|Prep|SVA|Vform)\$";
}

use Data::Dumper;

my @SENT;
my $ORIG;
while(<STDIN>) {
    chomp;
    if(/^S\s/) {
        if(@SENT) {
            printSent($ORIG, @SENT);
        }
        s/^S\s//;
        $ORIG = $_;
        @SENT = split(/\s/, $_);;
    }
    if(/^A\s/) {
        s/^A\s//;
        my ($span, $type, $sub, $req, $none, $annotator) = split(/\|\|\|/, $_);
        next if($PATTERN and $type !~ /$PATTERN/);
        next if $annotator != $ANNOT;

        my ($start, $end) = split(/\s/, $span);
        next if ($start < 0 and $end < 0);

        for(my $i = $start; $i < $end; $i++) {
            if($sub and $i == $start) {
                 $SENT[$i] = $sub;
            }
            else {
                $SENT[$i] = "\@DELETE ME\@";
            }
        }
        if($start == $end) {
            $SENT[$start] = "$sub $SENT[$start]";
        }
    }
}
if(@SENT) {
    printSent($ORIG, @SENT)
}

sub printSent {
    my ($source, @anot) = @_;
    my @left = grep { !/^\@DELETE ME\@$/ } @anot;
    if(@left) {
        print $source, "\t", join(" ",  @left), "\n"
    }
    else {
        print "$source\t$source\n";
    }
}
