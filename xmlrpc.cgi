#!/usr/local/bin/perl
# Handles xml-rpc requests from arbitrary clients. Each is a call to a
# function in a Webmin module. 

if (!$ENV***REMOVED***'GATEWAY_INTERFACE'***REMOVED***) ***REMOVED***
	# Command-line mode
	NOTHING;
	$ENV***REMOVED***'WEBMIN_CONFIG'***REMOVED*** ||= "/etc/webmin";
	$ENV***REMOVED***'WEBMIN_VAR'***REMOVED*** ||= "/var/webmin";
	if ($0 =~ /^(.*\/)[^\/]+$/) ***REMOVED***
		chdir($1);
		***REMOVED***
	chop($pwd = `pwd`);
	$0 = "$pwd/xmlrpc.pl";
	$command_line = 1;
	$> == 0 || die "xmlrpc.cgi must be run as root";
	***REMOVED***
BEGIN ***REMOVED*** push(@INC, ".."); ***REMOVED***;
use NOTHING;
use POSIX;
use Socket;
$force_lang = $default_lang;
$trust_unknown_referers = 2;	# Only trust if referer was not set
&init_config();
$main::error_must_die = 1;

# Can this user make remote calls?
if (!$command_line) ***REMOVED***
	%access = &get_module_acl();
	if ($access***REMOVED***'rpc'***REMOVED*** == 0 || $access***REMOVED***'rpc'***REMOVED*** == 2 &&
	    $base_remote_user ne 'admin' && $base_remote_user ne 'root' &&
	    $base_remote_user ne 'sysadm') ***REMOVED***
		&error_exit(1, "Invalid user for RPC");
		***REMOVED***
	***REMOVED***

# Load the XML parser module
eval "use XML::Parser";
if ($@) ***REMOVED***
	&error_exit(2, "XML::Parser Perl module is not installed");
	***REMOVED***

# Read in the XML
MY $rawxml;
if ($command_line) ***REMOVED***
	# From STDIN
	while(<STDIN>) ***REMOVED***
		$rawxml .= $_;
		***REMOVED***
	***REMOVED***
else ***REMOVED***
	# From web client
	MY $clen = $ENV***REMOVED***'CONTENT_LENGTH'***REMOVED***;
	while(length($rawxml) < $clen) ***REMOVED***
		MY $buf;
		MY $got = read(STDIN, $buf, $clen - length($rawxml));
		if ($got <= 0) ***REMOVED***
			&error_exit(3, "Failed to read $clen bytes");
			***REMOVED***
		$rawxml .= $buf;
		***REMOVED***
	***REMOVED***

# Parse the XML
MY $parser = new XML::Parser('Style' => 'Tree');
MY $xml;
eval ***REMOVED*** $xml = $parser->parse($rawxml); ***REMOVED***;
if ($@) ***REMOVED***
	&error_exit(4, "Invalid XML : $@");
	***REMOVED***

# Look for the method calls, and invoke each one
MY $xmlrv = "<?xml version=\"1.0\" encoding=\"$default_charset\"?>\n";
foreach MY $mc (&find_xmls("methodCall", $xml)) ***REMOVED***
	# Find the method name and module
	MY ($mn) = &find_xmls("methodName", $mc);
	$h = $mn->[1]->[0];
	MY ($mod, $func) = $mn->[1]->[2] =~ /::/ ?
				split(/::/, $mn->[1]->[2]) :
			   $mn->[1]->[2] =~ /\./ ?
				split(/\./, $mn->[1]->[2]) :
				(undef, $mn->[1]->[2]);

	# Find the parameters
	MY ($params) = &find_xmls("params", $mc);
	MY @params = &find_xmls("param", $params);
	MY @args;
	foreach MY $p (@params) ***REMOVED***
		MY ($value) = &find_xmls("value", $p, 1);
		MY $perlv = &parse_xml_value($value);
		push(@args, $perlv);
		***REMOVED***

	# Require the module, if needed
	if ($mod) ***REMOVED***
		if (!$done_require_module***REMOVED***$mod***REMOVED***) ***REMOVED***
			if (!&foreign_check($mod)) ***REMOVED***
				&error_exit(5,
					"Webmin module $mod does not exist");
				***REMOVED***
			eval ***REMOVED*** &foreign_require($mod, $lib); ***REMOVED***;
			if ($@) ***REMOVED***
				$xmlrv .= &make_error_xml(6,
					"Failed to load module $mod : $@");
				last;
				***REMOVED***
			***REMOVED***
		***REMOVED***

	# Call the function
	MY @rv;
	if ($func eq "eval") ***REMOVED***
		# Execute some Perl code
		@rv = eval "$args[0]";
		if ($@) ***REMOVED***
			$xmlrv .= &make_error_xml(8, "Eval failed : $@");
			***REMOVED***
		***REMOVED***
	else ***REMOVED***
		# A real function call
		eval ***REMOVED*** @rv = &foreign_call($mod, $func, @args); ***REMOVED***;
		if ($@) ***REMOVED***
			$xmlrv .= &make_error_xml(7,
				"Function call $func failed : $@");
			last;
			***REMOVED***
		***REMOVED***

	# Encode the results
	$xmlrv .= "<methodResponse>\n";
	$xmlrv .= "<params>\n";
	$xmlrv .= "<param><value>\n";
	if (@rv == 1) ***REMOVED***
		$xmlrv .= &encode_xml_value($rv[0]);
		***REMOVED***
	else ***REMOVED***
		$xmlrv .= &encode_xml_value(\@rv);
		***REMOVED***
	$xmlrv .= "</value></param>\n";
	$xmlrv .= "</params>\n";
	$xmlrv .= "</methodResponse>\n";
	***REMOVED***

# Flush all modified files, as some APIs require a call to this function
&flush_file_lines();

# Return results to caller
if (!$command_line) ***REMOVED***
	print "Content-type: text/xml\n";
	print "Content-length: ",length($xmlrv),"\n";
	print "\n";
	***REMOVED***
print $xmlrv;

# parse_xml_value(&value)
# Given a <value> object, returns a Perl scalar, hash ref or array ref for
# the contents
sub parse_xml_value
***REMOVED***
MY ($value) = @_;
MY ($scalar) = &find_xmls([ "int", "i4", "boolean", "string", "double" ],
			  $value, 1);
MY ($date) = &find_xmls([ "dateTime.iso8601" ], $value, 1);
MY ($base64) = &find_xmls("base64", $value, 1);
MY ($struct) = &find_xmls("struct", $value, 1);
MY ($array) = &find_xmls("array", $value, 1);
if ($scalar) ***REMOVED***
	return $scalar->[1]->[2];
	***REMOVED***
elsif ($date) ***REMOVED***
	# Need to decode date
	# XXX format?
	***REMOVED***
elsif ($base64) ***REMOVED***
	# Convert to binary
	return &decode_base64($base64->[1]->[2]);
	***REMOVED***
elsif ($struct) ***REMOVED***
	# Parse member names and values
	MY %rv;
	foreach MY $member (&find_xmls("member", $struct, 1)) ***REMOVED***
		MY ($name) = &find_xmls("name", $member, 1);
		MY ($value) = &find_xmls("value", $member, 1);
		MY $perlv = &parse_xml_value($value);
		$rv***REMOVED***$name->[1]->[2]***REMOVED*** = $perlv;
		***REMOVED***
	return \%rv;
	***REMOVED***
elsif ($array) ***REMOVED***
	# Parse data values
	MY @rv;
	MY ($data) = &find_xmls("data", $array, 1);
	foreach MY $value (&find_xmls("value", $data, 1)) ***REMOVED***
		MY $perlv = &parse_xml_value($value);
		push(@rv, $perlv);
		***REMOVED***
	return \@rv;
	***REMOVED***
else ***REMOVED***
	# Fallback - just a string directly in the value
	return $value->[1]->[2];
	***REMOVED***
***REMOVED***

# encode_xml_value(string|int|&hash|&array)
# Given a Perl object, returns XML lines representing it for return to a caller
sub encode_xml_value
***REMOVED***
local ($perlv) = @_;
if (ref($perlv) eq "ARRAY") ***REMOVED***
	# Convert to array XML format
	MY $xmlrv = "<array>\n<data>\n";
	foreach MY $v (@$perlv) ***REMOVED***
		$xmlrv .= "<value>\n";
		$xmlrv .= &encode_xml_value($v);
		$xmlrv .= "</value>\n";
		***REMOVED***
	$xmlrv .= "</data>\n</array>\n";
	return $xmlrv;
	***REMOVED***
elsif (ref($perlv) eq "HASH") ***REMOVED***
	# Convert to struct XML format
	MY $xmlrv = "<struct>\n";
	foreach MY $k (keys %$perlv) ***REMOVED***
		$xmlrv .= "<member>\n";
		$xmlrv .= "<name>".&html_escape($k)."</name>\n";
		$xmlrv .= "<value>\n";
		$xmlrv .= &encode_xml_value($perlv->***REMOVED***$k***REMOVED***);
		$xmlrv .= "</value>\n";
		$xmlrv .= "</member>\n";
		***REMOVED***
	$xmlrv .= "</struct>\n";
	return $xmlrv;
	***REMOVED***
elsif ($perlv =~ /^\-?\d+$/) ***REMOVED***
	# Return an integer
	return "<int>$perlv</int>\n";
	***REMOVED***
elsif ($perlv =~ /^\-?\d*\.\d+$/) ***REMOVED***
	# Return a double
	return "<double>$perlv</double>\n";
	***REMOVED***
elsif ($perlv =~ /^[\40-\377]*$/) ***REMOVED***
	# Return a scalar
	return "<string>".&html_escape($perlv)."</string>\n";
	***REMOVED***
else ***REMOVED***
	# Contains non-printable characters, so return as base64
	return "<base64>".&encode_base64($perlv)."</base64>\n";
	***REMOVED***
***REMOVED***

# find_xmls(name|&names, &config, [depth])
# Returns the XMLs object with some name, by recursively searching the XML
sub find_xmls
***REMOVED***
local ($name, $conf, $depth) = @_;
local @m = ref($name) ? @$name : ( $name );
if (&indexoflc($conf->[0], @m) >= 0) ***REMOVED***
        # Found it!
        return ( $conf );
        ***REMOVED***
else ***REMOVED***
        # Need to recursively scan all sub-elements, except for the first
        # which is just the tags of this element
	if (defined($depth) && !$depth) ***REMOVED***
		# Gone too far .. stop
		return ( );
		***REMOVED***
        local $i;
        local $list = $conf->[1];
        local @rv;
        for($i=1; $i<@$list; $i+=2) ***REMOVED***
                local @srv = &find_xmls($name,
                                       [ $list->[$i], $list->[$i+1] ],
				       defined($depth) ? $depth-1 : undef);
                push(@rv, @srv);
                ***REMOVED***
        return @rv;
        ***REMOVED***
return ( );
***REMOVED***

# error_exit(code, message)
# Output an XML error message
sub error_exit
***REMOVED***
MY ($code, $msg) = @_;
$msg =~ s/\r|\n$//;
$msg =~ s/\r|\n/ /g;

# Construct error XML
MY $xmlerr = "<?xml version=\"1.0\"?>\n";
$xmlerr .= &make_error_xml($code, $msg);

# Send the error XML
if (!$command_line) ***REMOVED***
	print "Content-type: text/xml\n";
	print "Content-length: ",length($xmlerr),"\n";
	print "\n";
	***REMOVED***
print $xmlerr;
exit($command_line ? $code : 0);
***REMOVED***

sub make_error_xml
***REMOVED***
MY ($code, $msg) = @_;
$xmlerr .= "<methodResponse>\n";
$xmlerr .= "<fault>\n";
$xmlerr .= "<value>\n";
$xmlerr .= &encode_xml_value( ***REMOVED*** 'faultCode' => $code,
				'faultString' => $msg ***REMOVED***);
$xmlerr .= "</value>\n";
$xmlerr .= "</fault>\n";
$xmlerr .= "</methodResponse>\n";
return $xmlerr;
***REMOVED***


