<?php

$KEYS = array(
'2' => '292d2aefc02fbadcd4a44a989329aac97d53',
'3' => '9ed1d51d54535f6320e7252e08b3a29b227a',
'4' => '019c3044fb2e9edc7e1166c3bb3db931799c',
'5' => 'e33393b3621e4ea7bc04683ef9dc65841601',
'6' => '5aa891a79e529573f7016440a7d69cb1094d',
'7' => '98630ef6bb60b0bbad5ebd559f6ebdc9f65e',
'8' => '0044cbc74c85cb14a45a6bee20a6c17ec1f6',
'9' => 'ad6708c847da185684c3e89c65b14e6b3131',
'10' => 'fd2c670bae9b177de3d6f5cff184d5a5090a',
'11' => 'db92422b2cf4ce8cb4d6761697171b95b7fa',
'12' => '122b06da9a8080c4ce312a1d68f7035c9a58',
'13' => '6412f1a2eb57e1fc2d8c7a33e14db4c1e0e0',
'14' => '3859793567a5dfd0e007fe35b100aed46c1e',
'15' => 'abb4b52ce4784cff2f8ba5e2e373273d555a',
'16' => 'b5aaff37d5f576e3fb6b4685801d36b652d5',
'17' => '6388bb487e77f312c759483198cc243e0ecf',
'18' => '14502946a276366cd7f873e12d2c7b673137',
'19' => '1f9c7959af2869d31c931406fcc6f0576465',
'20' => '9d6e4db1835d291187b01c0b91b97431e4b5',
'21' => '6a497af552409ed457191a9d446fe2ec56d4',
'22' => '6c03d0d6b754b944705e28ad7a7c15780bd6',
'23' => 'f967ca147df007973535e2b4f93c71639439'
);


echo <<<EOT
<?php
/*
 * encryption_key:
EOT;
echo $KEYS[$_GET['t']];
echo <<<EOT
 *
 * part of pfSense (https://www.pfsense.org)
 * Copyright (c) 2003-2006 Manuel Kasper <mk@neon1.net>
 * Copyright (c) 2005-2006 Bill Marquette <bill.marquette@gmail.com>
 * Copyright (c) 2006 Paul Taylor <paultaylor@winn-dixie.com>
 * Copyright (c) 2004-2018 Rubicon Communications, LLC (Netgate)
 * All rights reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

include_once("auth.inc");
include_once("priv.inc");
if (!function_exists('platform_booting')) {
	require_once('globals.inc');
}
require_once('pfsense-utils.inc');

/* Authenticate user - exit if failed */
if (!session_auth()) {
	display_login_form();
	exit;
}

phpsession_begin();

/*
 * Once here, the user has authenticated with the web server.
 * We give them access only to the appropriate pages based on
 * the user or group privileges.
 */
$allowedpages = getAllowedPages($_SESSION['Username'], $_SESSION['user_radius_attributes']);

/*
 * Get user-based preference settings so they can be easily referenced.
 */
$user_settings = get_user_settings($_SESSION['Username']);

/*
 * redirect to first allowed page if requesting a wrong url
 */

/* Fix this up otherwise the privilege check will fail. See Redmine #5909. */
if ($_SERVER['REQUEST_URI'] == "/") {
	$_SERVER['REQUEST_URI'] = "/index.php";
}

if (!isAllowedPage($_SERVER['REQUEST_URI'])) {
	if (count($allowedpages) > 0) {
		$page = str_replace('*', '', $allowedpages[0]);
		$_SESSION['Post_Login'] = true;
		require_once("functions.inc");
		pfSenseHeader("/{$page}");

		$username = get_config_user();
		log_error("{$username} attempted to access {$_SERVER['SCRIPT_NAME']} but does not have access to that page. Redirecting to {$page}.");

		exit;
	} else {
		// add this so they don't get stuck on the logout page when they have no permissions.
		$_SESSION["Logged_In"] = false;
		display_error_form("201", gettext("No page assigned to this user! Click here to logout."));

		exit;
	}
} else {
	$_SESSION['Post_Login'] = true;
}

/*
 * redirect browsers post-login to avoid pages
 * taking action in response to a POST request
 */
if (!$_SESSION['Post_Login']) {
	$_SESSION['Post_Login'] = true;
	require_once("functions.inc");
	pfSenseHeader($_SERVER['REQUEST_URI']);
	exit;
}

/*
 * Close session data to allow other scripts from same host to come in.
 * A session can be reactivated from calling phpsession_begin again
 */
phpsession_end(true);

/*
 * determine if the user is allowed access to the requested page
 */
function display_error_form($http_code, $desc) {
	global $config, $user_settings, $g;

	if (isAjax()) {
		printf(gettext('Error: %1$s Description: %2$s'), $http_code, $desc);
		return;
	}

	$logincssfile = "#770101";
?>

<!DOCTYPE html>
<html lang="en">
	<head>
		<meta name="viewport" content="width=device-width, initial-scale=1">
	    <link rel="stylesheet" href="/vendor/bootstrap/css/bootstrap.min.css" type="text/css">
	    <link rel="stylesheet" href="/css/login.css?v=<?=filemtime('/usr/local/www/css/login.css')?>" type="text/css">
		<title><?=gettext("Error"); ?></title>
	</head>

	<body id="error" >
		<div id="total">
			<header>
				<div id="headerrow">
					<div class="row">
						<div class="col-sm-4">
							<div id="logodiv" style="text-align:center" class="nowarning">
								<?php include("/usr/local/www/logo.svg"); ?>
							</div>
						</div>
						<div class="col-sm-8 nowarning msgbox text-center">
							<span id="hostspan">
							</span>
						</div>
					</div>
				</div>
			</header>

			<div style="background: <?=$logincssfile?>;" class="pagebody">
				<div class="col-sm-2"></div>

				<div class="col-sm-8 offset-md-4 logoCol">
					<div class="loginCont center-block error-panel">
						<a href="index.php?logout"><?=$desc;?></a>
					</div>
				</div>

			<div class="col-sm-2"></div>
			</div>

			<footer id="3">
			<div id="footertext">
					<p class="text-muted">
						<?=print_credit()?>
					</p>
				</div>
			</footer>
		</div>
	</body>
</html>

<?php

} // end function


function display_login_form() {
	require_once("globals.inc");
	global $config, $g;

	unset($input_errors);

	if (isAjax()) {
		if (isset($_POST['login'])) {
			if ($_SESSION['Logged_In'] <> "True") {
				isset($_SESSION['Login_Error']) ? $login_error = $_SESSION['Login_Error'] : $login_error = gettext("unknown reason");
				printf("showajaxmessage('" . gettext("Invalid login (%s).") . "')", $login_error);
			}
			if (file_exists("{$g['tmp_path']}/webconfigurator.lock")) {
				// TODO: add the IP from the user who did lock the device
				$whom = file_get_contents("{$g['tmp_path']}/webconfigurator.lock");
				printf("showajaxmessage('" . gettext("This device is currently being maintained by: %s.") . "');", $whom);
			}
		}
		//If session ended
		echo "SESSION_TIMEOUT";
		exit;
	}

	/* Check against locally configured IP addresses, which will catch when someone
	   port forwards WebGUI access from WAN to an internal IP on the router. */
	global $FilterIflist, $nifty_background;

	$local_ip = false;

	if (strpos($_SERVER['HTTP_HOST'], ":") === FALSE) {
		$http_host_port = explode(":", $_SERVER['HTTP_HOST']);
		$http_host = $http_host_port[0];
	} else {
		$http_host = $_SERVER['HTTP_HOST'];
	}

	if (empty($FilterIflist)) {
		require_once('filter.inc');
		require_once('shaper.inc');
		filter_generate_optcfg_array();
	}

	foreach ($FilterIflist as $iflist) {
		if ($iflist['ip'] == $http_host) {
			$local_ip = true;
		} else if ($iflist['ipv6'] == $http_host) {
			$local_ip = true;
		} else if (is_array($iflist['vips'])) {
			foreach ($iflist['vips'] as $vip) {
				if ($vip['ip'] == $http_host) {
					$local_ip = true;
					break;
				}
			}

			unset($vip);
		}

		if ($local_ip == true) {
			break;
		}
	}

	unset($FilterIflist);
	unset($iflist);

	if ($local_ip == false) {
		if (is_array($config['openvpn']['openvpn-server'])) {
			foreach ($config['openvpn']['openvpn-server'] as $ovpns) {
				if (is_ipaddrv4($http_host) && !empty($ovpns['tunnel_network']) && ip_in_subnet($http_host, $ovpns['tunnel_network'])) {
					$local_ip = true;
				} else if (is_ipaddrv6($http_host) && !empty($ovpns['tunnel_networkv6']) && ip_in_subnet($http_host, $ovpns['tunnel_networkv6'])) {
					$local_ip = true;
				}

				if ($local_ip == true) {
					break;
				}
			}
		}
	}

	// For the login form, get the settings of no particular user.
	// That ensures we will use the system default theme for the login form.
	$user_settings = get_user_settings("");
	$cssfile = "/css/pfSense.css";

	if (isset($user_settings['webgui']['webguicss'])) {
		if (file_exists("/usr/local/www/css/" . $user_settings['webgui']['webguicss'])) {
			$cssfile = "/css/" . $user_settings['webgui']['webguicss'];
		}
	}

	$logincssfile = "#1e3f75";

	if (isset($user_settings['webgui']['logincss']) && strlen($user_settings['webgui']['logincss']) == 6) {
		$logincssfile = "#" . $user_settings['webgui']['logincss'];
	}

	if (isset($config['system']['webgui']['loginshowhost'])) {
		$loginbannerstr = sprintf(gettext('%1$s.%2$s'), htmlspecialchars($config['system']['hostname']), htmlspecialchars($config['system']['domain']));
	} else {
		$loginbannerstr = sprintf(gettext('Login to %1$s'), $g['product_name']);
	}

	$loginautocomplete = isset($config['system']['webgui']['loginautocomplete']) ? '' : 'autocomplete="off"';

	if (is_ipaddr($http_host) && !$local_ip && !isset($config['system']['webgui']['nohttpreferercheck'])) {
		$warnclass = "pagebodywarn";	// Make room for a warning display row
	} else {
		$warnclass = "pagebody";
	}
?>
<!DOCTYPE html>
<html lang="en">
	<head>
		<meta name="viewport" content="width=device-width, initial-scale=1">
	    <link rel="stylesheet" href="/vendor/bootstrap/css/bootstrap.min.css" type="text/css">
	    <link rel="stylesheet" href="/css/login.css?v=<?=filemtime('/usr/local/www/css/login.css')?>" type="text/css">
		<title><?=gettext("Login"); ?></title>
		<script type="text/javascript">
			//<![CDATA{
			var events = events || [];
			//]]>
		</script>
	</head>

	<body id="login" >
		<div id="total">
			<header>
				<div id="headerrow">
					<div class="row">
						<!-- Header left logo box -->
						<div class="col-sm-4">
							<div id="logodiv" style="text-align:center" class="nowarning">
								<?php include("/usr/local/www/logo.svg"); ?>
							</div>
						</div>

						<!-- Header center message box -->
						<div class="col-sm-4 nowarning msgbox text-center text-danger">
<?php
						if (!empty($_POST['usernamefld'])) {
							print("<h4>" . $_SESSION['Login_Error'] . "</h4>");
						}
?>
						</div>

						<!-- Header right message box (hostname or msg)-->
						<div class="col-sm-4 nowarning msgbox text-center">
							<span id="hostspan">
								<a><h4><?=$loginbannerstr?></h4></a>
							</span>
						</div>
					</div>
<?php
	if ($warnclass == "pagebodywarn") {
?>
					<div class="row">
						<div class="col-sm-12">
							<div class="alert alert-warning <?=$warnclass?>">
								<?=gettext("The IP address being used to access this router is not configured locally, which may be forwarded by NAT or other means.
								If this forwarding is unexpected, it should be verified that a man-in-the-middle attack is not taking place.")?>
							</div>
						</div>
					</div>
<?php
	}
?>
	            </div>
	        </header>

	        <div style="background: <?=$logincssfile?>;" class="<?=$warnclass?>">
	        	<div class="col-sm-4"></div>

	        	<div class="col-sm-4 offset-md-4 logoCol">
					<div class="loginCont center-block">
		                <form method="post" <?=$loginautocomplete?> class="login">
			                <p class="form-title">Sign In</p>
			                <input name="usernamefld" id="usernamefld" type="text" placeholder="Username" autocorrect="off" autocapitalize="none"/>
			                <input name="passwordfld" id="passwordfld" type="text" placeholder="Password" readonly/>
			                <input type="submit" name="login" value="Sign In" class="btn btn-success btn-sm" />
		                </form>
					</div>
	            </div>

	        	<div class="col-sm-4"></div>
	        </div>

	        <footer id="3">
	            <div id="footertext">
					<p class="text-muted">
						<?=print_credit()?>
					</p>
	            </div>
	        </footer>
	    </div>

		<script src="/vendor/jquery/jquery-1.12.0.min.js?v=<?=filemtime('/usr/local/www/vendor/jquery/jquery-1.12.0.min.js')?>"></script>
		<script src="/vendor/bootstrap/js/bootstrap.min.js?v=<?=filemtime('/usr/local/www/vendor/bootstrap/js/bootstrap.min.js')?>"></script>
		<script src="/js/pfSense.js?v=<?=filemtime('/usr/local/www/js/pfSense.js')?>"></script>

		<script type="text/javascript">
		//!<[CDATA[
		events.push(function() {
			document.cookie=
				"cookie_test=1" +
				"<?php echo $config['system']['webgui']['protocol'] == 'https' ? '; secure' : '';?>";

			if (document.cookie.indexOf("cookie_test") == -1) {
				alert("<?=gettext('The browser must support cookies to login.')?>");
			}

			// Delete it
			document.cookie = "cookie_test=1; expires=Thu, 01-Jan-1970 00:00:01 GMT";
		});
		//]]>
		</script>

	</body>
</html>

<?php
} // end function
EOT;
?>
