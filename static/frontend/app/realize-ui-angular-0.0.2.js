/**
 * realize-ui-angular - v0.0.2 - 2014-04-03
 * https://github.com/realizeapp/realize-ui-angular
 *
 * Copyright (c) 2014 Realize
 * Licensed AGPL <https://raw.github.com/realizeapp/realize-ui-angular/master/LICENSE>
 */
(function ( window, angular, undefined ) {

define([
	'angular',
	'angularAMD',
	'jquery',
	'spin',
	'ngTouch',
	'angular-ui-bootstrap',
	'realize-debugging',
	'user',
	'widget',
	'lodash',
	'realize-lodash',
	'angular-charts',
	'moment',
	'ngRoute',
	'angular-formly',
	'screen',
	'ngload',
	'view',
	'context',
	'plugin',
	'util',
	'angular-growl',
	'error',
	'angular-gridster',
	'realize-sync',
	'angular-spinner',
    'angular-leaflet'
], function (angular, angularAMD, $, Spinner) {
	var DEBUG_MODE = false;

	var module = angular.module('realize', ['ui.bootstrap', 'realize-debugging', 'http-auth-interceptor', 'user', 'widget', 'realize-lodash', 'angularCharts', 'ngRoute', 'formly', 'screen', 'view', 'context', 'plugin', 'util', 'angular-growl', 'error', 'gridster', 'realize-sync', 'angularSpinner', 'leaflet-directive'])
		.constant('EVENTS', {
			// auth
			loginSuccess: 'event:auth-loginConfirmed',
			loginFailed: 'event:auth-login-failed',
			logoutSuccess: 'event:auth-logout-success',
			logoutAttempt: 'event:auth-logout-attempt',
			tokenExpired: 'event:auth-token-expired',
			notAuthenticated: 'event:auth-loginRequired',
			notAuthorized: 'event:auth-not-authorized',
			switchWidgetTree: 'event:widget-replace-tree',
			widgetSettingsChange: 'event:widget-change-settings',
			widgetRefreshPressed: 'event:widget-refresh',
			widgetRenderData: 'event:widget-render',
			widgetViewChange: 'event:widget-view-change',
			widgetAddToDash: 'event:widget-add-to-dash'
		})

		.constant('USER_ROLES', {
			all: '*',
			admin: 'admin',
			guest: 'guest'
		})

		.config(['$locationProvider', '$controllerProvider', '$compileProvider', '$routeProvider', '$provide',
			function ($locationProvider, $controllerProvider, $compileProvider, $routeProvider, $provide) {
				// for debugging purposes, log all events emitted to rootscope.
				$provide.decorator('$rootScope', ['$delegate', function ($delegate) {
					var emit = $delegate.$emit;

					$delegate.$emit = function () {
						console.log.apply(console, arguments);
						emit.apply(this, arguments);
					};

					return $delegate;
				}]);
				// enable pushstate so urls are / instead of /#/ as root
				$locationProvider.html5Mode(true);


				$routeProvider
					.when('/', { template: '', controller: 'WidgetRouteCtrl'})
					.when('/:type', { template: '', controller: 'WidgetRouteCtrl'})
					.when('/:type/:name', { template: '', controller: 'WidgetRouteCtrl'})
					.otherwise({
						redirectTo: '/'
					});

				$provide.decorator('$rootScope', ['$delegate', function ($delegate) {

					Object.defineProperty($delegate.constructor.prototype, '$onRootScope', {
						value: function (name, listener) {
							var unsubscribe = $delegate.$on(name, listener);
							this.$on('$destroy', unsubscribe);
						},
						enumerable: false
					});


					return $delegate;
				}]);
			}
		])


		// run is where we set initial rootscope properties
		.run(['$rootScope', 'user', 'EVENTS', '$window', function ($root, user, EVENTS, $window) {

			// check user auth status on initial pageload
			$root.authed = user.isAuthed();

			$root.$watch(user.isAuthed, function (newVal, oldVal) {
				$root.authed = newVal;
			});

			$root.closeMenus = function () {
				var open = false;
				if ($root.showleftmenu) {
					open = true;
					$root.showleftmenu = 0;
				}
				if ($root.showrightmenu) {
					open = true;
					$root.showrightmenu = 0;
				}
				return open;
			};

			$window.Spinner = Spinner;
		}
		])

		.filter('capitalize', [function () {
			return function (input, scope) {
				if (input !== null) {
					input = input.toLowerCase();
				}

				return input.substring(0, 1).toUpperCase() + input.substring(1);
			};
		}])

		.factory('$exceptionHandler', ['error', function (error) {
			return function (exception, cause) {
				error.handleException(exception, cause);
			};
		}]);
	return module;
});
require(['angularAMD', 'app', 'controllers', 'directives'], function (angularAMD, app) {
	angularAMD.bootstrap(app, true, document);
});
angular.module('html_templates_jsfied', ['partials/left-menu.tpl.html', 'partials/plugin-list-item.tpl.html', 'partials/plugin-list.tpl.html', 'partials/right-menu.tpl.html', 'partials/top-nav.tpl.html', 'partials/views/chart.tpl.html', 'partials/views/form.tpl.html', 'partials/views/map.tpl.html', 'partials/views/number.tpl.html', 'partials/views/text.tpl.html', 'partials/widget-container.tpl.html', 'partials/widget-content.tpl.html']);

angular.module("partials/left-menu.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("partials/left-menu.tpl.html",
    "<div class=\"menuleft\"\n" +
    "			ng-class=\"{active:$root.showleftmenu}\"\n" +
    "			ng-click=\"$event.stopPropagation();\" ng-controller=\"LeftMenuCtrl\">\n" +
    "\n" +
    "\n" +
    "	<div class=\"content-container\" ng-class='{active:shownItem}'>\n" +
    "		<ul class=\"nav nav-pils nav-stacked\" ng-if=\"authed\">\n" +
    "			<li ng-click=\"showItem('settings')\">\n" +
    "				<a class=\"fa fa-angle-right\"></a>\n" +
    "				<a>Settings</a>\n" +
    "			</li>\n" +
    "			<li ng-click=\"showItem('authorizations')\">\n" +
    "				<a class=\"fa fa-angle-right\"></a>\n" +
    "				<a>Authorizations</a>\n" +
    "			</li>\n" +
    "			<li ng-click=\"showItem('contact')\">\n" +
    "				<a class=\"fa fa-angle-right\"></a>\n" +
    "				<a>Contact Us</a>\n" +
    "			</li>\n" +
    "            <li ng-click=\"showItem('developers')\">\n" +
    "				<a class=\"fa fa-angle-right\"></a>\n" +
    "				<a>Developers</a>\n" +
    "			</li>\n" +
    "            <li ng-click=\"logout();\">\n" +
    "				<a>Log Out</a>\n" +
    "			</li>\n" +
    "		</ul>\n" +
    "		<div class=\"left-menu-content\">\n" +
    "			<button class=\"btn btn-link\" ng-click=\"shownItem=''\">\n" +
    "				<span class=\"fa fa-angle-left\"></span>\n" +
    "				<span>Back</span>\n" +
    "			</button>\n" +
    "			<div class=\"leftmenuitembody settings\" ng-class=\"{active:shownItem==='settings'}\">\n" +
    "				<form class=\"app-settings\">\n" +
    "					<label for=\"timezone\">Time Zone</label>\n" +
    "					<input name=\"timezone\" type=\"text\" placeholder=\"Time Zone\"></input>\n" +
    "				</form>\n" +
    "			</div>\n" +
    "			<div class=\"leftmenuitembody developers\" ng-class=\"{active:shownItem==='developers'}\">\n" +
    "				<p>Want to customize Realize?  Check us out on <a href=\"http://www.github.com/realizeapp/realize-core\">Github</a>!</p>\n" +
    "			</div>\n" +
    "			<div class=\"leftmenuitembody authorizations\" ng-class=\"{active:shownItem==='authorizations'}\">\n" +
    "               <ul class=\"authorization-list\">\n" +
    "                    <li ng-repeat=\"auth in authorizationList\">\n" +
    "                      <a ng-click=\"authRedirect(auth)\"><span ng-class=\"(auth.active==true) ? 'fa fa-minus' : 'fa fa-plus'\"></span> {{auth.name | capitalize}}</a>\n" +
    "                    </li>\n" +
    "               </ul>\n" +
    "			</div>\n" +
    "			<div class=\"leftmenuitembody contact\" ng-class=\"{active:shownItem==='contact'}\">\n" +
    "                <p>Have idea, suggestions, comments? Give us feedback and vote on suggested features with <a href=\"realize.uservoice.com\">Uservoice</a>.</p>\n" +
    "				<p>Have a question or want to reach us directly?  Email us at <a href=\"mailto:hello@realize.pe\" target=\"_top\">hello@realize.pe</a>.</p>\n" +
    "			</div>\n" +
    "			<div class=\"leftmenuitembody feedback\" ng-class=\"{active:shownItem==='feedback'}\">\n" +
    "\n" +
    "			</div>\n" +
    "		</div>\n" +
    "	</div>\n" +
    "</div>\n" +
    "");
}]);

angular.module("partials/plugin-list-item.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("partials/plugin-list-item.tpl.html",
    "<div class=\"plugin-list-item\">\n" +
    "    <div class=\"plugin-heading\">\n" +
    "        <div class=\"btn-group plugin-actions\">\n" +
    "            <a class=\"plugin-add btn btn-default\" ng-if=\"type === 'plugins'\" ng-click=\"(item.installed==true) ? remove(item) : add(item)\"><span ng-class=\"(item.installed==true) ? 'fa fa-minus' : 'fa fa-plus'\"> {{(item.installed==true) ? 'Remove' : 'Add'}}</span></a>\n" +
    "             <a class=\"widget-add btn btn-default\" ng-if=\"type === 'widgets'\" ng-click=\"add(item)\"><span class=\"fa fa-plus\"> Add</span></a>\n" +
    "            <a class=\"plugin-info btn btn-default\" ng-click=\"info(item)\"><span class=\"fa fa-question-circle\"></span> More Info</a>\n" +
    "        </div>\n" +
    "        <h4 ng-if=\"type === 'plugins'\">{{item.name | capitalize}}</h4>\n" +
    "        <h4 ng-if=\"type === 'widgets'\">{{item.title}}</h4>\n" +
    "        <p>{{item.description}}</p>\n" +
    "    </div>\n" +
    "    <div class=\"plugin-body\">\n" +
    "        <div class=\"required\" ng-if=\"item.deps.required.length > 0\">\n" +
    "            <div class=\"dependency\">\n" +
    "                <h5>Requires</h5>\n" +
    "            </div>\n" +
    "           <div ng-repeat=\"req in item.deps.required\" class=\"dependency\">\n" +
    "               {{req}}\n" +
    "           </div>\n" +
    "       </div>\n" +
    "    </div>\n" +
    "</div>");
}]);

angular.module("partials/plugin-list.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("partials/plugin-list.tpl.html",
    "<div class=\"plugin-list\" ng-controller=\"ExtensionCtrl\">\n" +
    "    <div class=\"search-box\">\n" +
    "        <label>\n" +
    "            Search\n" +
    "            <input type=\"text\" ng-model=\"query\">\n" +
    "        </label>\n" +
    "    </div>\n" +
    "    <plugin-list-item ng-repeat=\"item in items | filter:query\"></plugin-list-item>\n" +
    "</div>");
}]);

angular.module("partials/right-menu.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("partials/right-menu.tpl.html",
    "<div class=\"menuright\"\n" +
    "		ng-class=\"{active:$root.showrightmenu}\"\n" +
    "		ng-click=\"$event.stopPropagation();\"\n" +
    "		ng-controller=\"RightMenuCtrl\">\n" +
    "	<button class=\"btn btn-link\" ng-click=\"$root.showrightmenu=0\">\n" +
    "		<span class=\"fa fa-angle-right\"></span>\n" +
    "		<span>Close</span>\n" +
    "	</button>\n" +
    "	<plugin-list></plugin-list>\n" +
    "</div>");
}]);

angular.module("partials/top-nav.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("partials/top-nav.tpl.html",
    "<div class=\"top-nav\" ng-controller=\"TopNavCtrl\">\n" +
    "	<nav class=\"navbar navbar-default\" role=\"navigation\">\n" +
    "\n" +
    "		<div class=\"container\">\n" +
    "				<!-- If User Authed -->\n" +
    "				<ul class=\"nav navbar-nav\" ng-if=\"authed\">\n" +
    "					<li class=\"navbar-link\">\n" +
    "						<a ng-click=\"$root.showleftmenu=!$root.showleftmenu;$event.stopPropagation();\"\n" +
    "								class=\"nav-toggle-left navbar-brand\">\n" +
    "                            <span class=\"fa fa-bars\"></span>\n" +
    "                            Realize\n" +
    "						</a>\n" +
    "					</li>\n" +
    "					<li class=\"dashboard-dropdown dropdown\" ng-controller=\"DashboardsCtrl\">\n" +
    "						<a class=\"dropdown-toggle\">\n" +
    "							<span class=\"fa fa-dashboard\"></span>\n" +
    "							<span class=\"navbar-link\">Dashboards</span>\n" +
    "						</a>\n" +
    "						<ul class=\"dropdown-menu\">\n" +
    "              <li ng-repeat=\"dash in dashboards\" ng-click=\"switchDashboard(dash.name)\">\n" +
    "								<a class=\"navbar-link\">\n" +
    "									<span class=\"dashboard-select-title\">{{dash.name | capitalize}}</span>\n" +
    "								</a>\n" +
    "							</li>\n" +
    "						</ul>\n" +
    "					</li>\n" +
    "					<li class=\"realize-market navbar-link nav-toggle-right\"\n" +
    "							ng-click=\"$root.showrightmenu=!$root.showrightmenu;$event.stopPropagation();\">\n" +
    "						<a class=\"fa fa-gear\"><span class=\"hidden-xs navbar-link\">Market</span></a>\n" +
    "					</li>\n" +
    "				</ul>\n" +
    "\n" +
    "\n" +
    "				<!-- If !authed -->\n" +
    "				<ul class=\"nav navbar-nav\" ng-if=\"!authed\">\n" +
    "					<li class=\"navbar-link\">\n" +
    "						<a href=\"/\" class=\"navbar-brand\">\n" +
    "                            Realize\n" +
    "						</a>\n" +
    "					</li>\n" +
    "					<li class=\"nav-register\" ng-click=\"register()\">\n" +
    "						<a class=\"navbar-link\"><span class=\"fa fa-user\"></span> <span class=\"hidden-xs\">Sign Up</span></a>\n" +
    "					</li>\n" +
    "					<li class=\"nav-login\" ng-click=\"login()\">\n" +
    "						<a class=\"navbar-link\"><span class=\"fa fa-sign-in\"></span> <span class=\"hidden-xs\">Log In</span></a>\n" +
    "					</li>\n" +
    "					<li class=\"nav-about\" ng-click=\"about()\">\n" +
    "						<a class=\"navbar-link\"><span class=\"fa fa-question-circle\"></span> <span class=\"hidden-xs\">About</span></a>\n" +
    "					</li>\n" +
    "                    <li class=\"nav-about\">\n" +
    "						<a class=\"navbar-link\" href=\"http://www.github.com/realizeapp/realize-core\" target=\"_blank\"><span class=\"fa fa-flask\"></span> <span class=\"hidden-xs\">Developers</span></a>\n" +
    "					</li>\n" +
    "				</ul>\n" +
    "\n" +
    "		</div>\n" +
    "\n" +
    "\n" +
    "	</nav>\n" +
    "</div>");
}]);

angular.module("partials/views/chart.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("partials/views/chart.tpl.html",
    "<div ng-if=\"data.chartData !== undefined\">\n" +
    "    <div ac-chart=\"data.chartType\" ac-data=\"data.chartData\" ac-config=\"data.chartConfig\" class='chart'></div>\n" +
    "</div>");
}]);

angular.module("partials/views/form.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("partials/views/form.tpl.html",
    "<div ng-if=\"data.formData !== undefined\">\n" +
    "    <formly-form result=\"formData\" fields=\"formFields\" options=\"formOptions\" ng-submit=\"save()\">\n" +
    "    </formly-form>\n" +
    "</div>");
}]);

angular.module("partials/views/map.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("partials/views/map.tpl.html",
    "<div ng-if=\"data.chartData !== undefined\">\n" +
    "    <div ac-chart=\"data.chartType\" ac-data=\"data.chartData\" ac-config=\"data.chartConfig\" class='chart'></div>\n" +
    "</div>");
}]);

angular.module("partials/views/number.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("partials/views/number.tpl.html",
    "<div>{{ data.number }}</div>");
}]);

angular.module("partials/views/text.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("partials/views/text.tpl.html",
    "<div>{{ data.text }}</div>");
}]);

angular.module("partials/widget-container.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("partials/widget-container.tpl.html",
    "<div class=\"widget\" ng-class=\"(widgetData.name.substring(0, 8) === 'realize_') ? '' : 'widget-border'\">\n" +
    "	<div class=\"widget-heading auth\" ng-controller=\"WidgetActionsCtrl\">\n" +
    "		<div class=\"widget-actions\" ng-show=\"widgetData.settings !== undefined\">\n" +
    "			<div ng-show=\"widgetData.display !== undefined && widgetData.display.views !== undefined\" class=\"widget-action dropdown\">\n" +
    "				<a class=\"btn btn-default dropdown-toggle\">\n" +
    "					<span class=\"fa fa-caret-down\"></span>\n" +
    "				</a>\n" +
    "				<ul class=\"dropdown-menu\">\n" +
    "					<li ng-repeat=\"(key, value) in widgetData.display.views\">\n" +
    "						<a ng-click=\"changeView(key)\">{{key}}</a>\n" +
    "					</li>\n" +
    "				</ul>\n" +
    "			</div>\n" +
    "\n" +
    "			<div class=\"widget-action\">\n" +
    "				  <a class=\"btn btn-default\" ng-click=\"refreshWidget()\"><span class=\"fa fa-refresh\" ></span> </a>\n" +
    "			</div>\n" +
    "\n" +
    "			<div class=\"widget-action\">\n" +
    "					<a class=\"btn btn-default\" ng-click=\"showSettings()\"><span class=\"fa fa-gear\" ></span> </a>\n" +
    "			</div>\n" +
    "\n" +
    "			<div class=\"widget-action\">\n" +
    "					<a class=\"btn btn-default\" ng-click=\"deleteWidget()\"><span class=\"fa fa-trash-o\" ></span> </a>\n" +
    "			</div>\n" +
    "		</div>\n" +
    "\n" +
    "		<div collapse=\"collapseSettings\">\n" +
    "			<formly-form result=\"formData\" fields=\"fields\" options=\"formOptions\" ng-submit=\"save()\">\n" +
    "			</formly-form>\n" +
    "		</div>\n" +
    "\n" +
    "	</div>\n" +
    "	<div class=\"widget-body widget-content\">\n" +
    "        <span us-spinner ng-if=\"widgetData === undefined\"></span>\n" +
    "		<ng-include src=\"widgetData.template\" widgetData=\"{{widgetData}}\"></ng-include>\n" +
    "	</div>\n" +
    "</div>");
}]);

angular.module("partials/widget-content.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("partials/widget-content.tpl.html",
    "<span us-spinner ng-if=\"data === undefined\"></span>\n" +
    "<div ng-include=\"template\" ng-if=\"data !== undefined\"></div>");
}]);

var config = {
	paths: {
		// Tests
		'appSpec': 'app.spec.js',

		// Third party
		'angular': 'thirdparty/angular/angular',
		'angular-ui-router': 'thirdparty/angular-ui-router/release/angular-ui-router',
		'jquery': 'thirdparty/jquery/jquery',
		'lodash': 'thirdparty/lodash/dist/lodash',
		'angular-ui-bootstrap': 'thirdparty/angular-bootstrap/ui-bootstrap-tpls',
		'angularMocks': 'thirdparty/angular-mocks/angular-mocks',
		'ngTouch': 'thirdparty/angular-touch/angular-touch',
		'http-auth-interceptor': 'thirdparty/angular-http-auth/src/http-auth-interceptor',
		'angularGesture': 'thirdparty/angular-gesture/ngGesture/gesture',
		'angularUIUtils': 'thirdparty/angular-ui-utils/modules/utils',
		'ngParse': 'thirdparty/requirejs-angular-define/src/ngParse',
		'angularAMD': 'thirdparty/angularAMD/angularAMD',
		'ngload': 'thirdparty/angularAMD/ngload',
		'd3': 'thirdparty/d3/d3.min',
		'angular-charts': 'thirdparty/angular-charts/dist/angular-charts.min',
		'moment': 'thirdparty/momentjs/min/moment.min',

		// Templates
		'html_templates_jsfied': 'html_templates_jsfied',

		// Core app modules
		'controllers': 'lib/app/controllers',
		'directives': 'lib/app/directives',

		// Common app modules
		'realize-debugging': 'lib/common/modules/debugging',
		'realize-sync': 'lib/common/modules/sync',
		'realize-mock-backend': 'lib/common/modules/mock-backend',
		'realize-lodash': 'lib/common/modules/lodash',

		// Common app models
		'widget': 'lib/common/models/widget',
		'user': 'lib/common/models/user'
	},
	shim: {
		'angular': {'deps': ['jquery'], 'exports': 'angular'},
		'angular-ui-router': ['angular'],
		'angularMocks': {
			deps: ['angular'],
			'exports': 'angular.mock'
		},
		'angular-charts': {
			deps: ['jquery', 'angular', 'd3']
		},
		'ngTouch': {
			deps: ['angular'],
			exports: 'ngTouch'
		},
		'angular-ui-bootstrap': {
			deps: ['angular']
		},
		'html_templates_jsfied': {
			deps: ['angular']
		},
		'http-auth-interceptor': {
			deps: ['angular']
		},
		'angularAMD': {
			deps: ['angular']
		},
		'ngload': {
			deps: ['angularAMD']
		}
	},
	priority: [
		"angular"
	]
};

require.config(config);

require(['angularAMD'], function (angularAMD) {

	// require the application
	require(['app', 'controllers', 'directives'], function (app) {

		// bootstrap the application
		angularAMD.bootstrap(app, true, document);
	});
});
require.config({
	paths: {
		// Third party
		'angular': 'thirdparty/angular/angular',
		'angular-ui-router': 'thirdparty/angular-ui-router/release/angular-ui-router',
		'jquery': 'thirdparty/jquery/jquery',
		'jquery-ui': 'thirdparty/jquery-ui/ui/minified/jquery-ui.min',
		'lodash': 'thirdparty/lodash/dist/lodash',
		'angular-ui-bootstrap': 'thirdparty/angular-bootstrap/ui-bootstrap-tpls',
		'angularMocks': 'thirdparty/angular-mocks/angular-mocks',
		'ngTouch': 'thirdparty/angular-touch/angular-touch',
		'http-auth-interceptor': 'thirdparty/angular-http-auth/src/http-auth-interceptor',
		'angularGesture': 'thirdparty/angular-gesture/ngGesture/gesture',
		'angularUIUtils': 'thirdparty/angular-ui-utils/modules/utils',
		'ngParse': 'thirdparty/requirejs-angular-define/src/ngParse',
		'angularAMD': 'thirdparty/angularAMD/angularAMD',
		'ngload': 'thirdparty/angularAMD/ngload',
		'd3': 'thirdparty/d3/d3.min',
		'angular-charts': 'thirdparty/angular-charts/dist/angular-charts.min',
		'moment': 'thirdparty/momentjs/min/moment.min',
		'ngRoute': 'thirdparty/angular-route/angular-route',
		'angular-formly': 'thirdparty/angular-formly/dist/formly',
		'angular-growl': 'thirdparty/angular-growl/build/angular-growl',
		'angular-animate': 'thirdparty/angular-animate/angular-animate',
		'angular-gridster': 'thirdparty/angular-gridster/dist/scripts/gridster.min',
		'es5-shim': 'thirdparty/es5-shim/es5-shim',
		'angular-spinner': 'thirdparty/angular-spinner/angular-spinner',
		'spin': 'thirdparty/spin.js/spin',
        'leaflet': 'thirdparty/leaflet-dist/leaflet',
        'angular-leaflet': 'thirdparty/angular-leaflet-directive/dist/angular-leaflet-directive',

		// Templates
		'html_templates_jsfied': 'html_templates_jsfied',

		// Core app modules
		'controllers': 'lib/app/controllers',
		'directives': 'lib/app/directives',

		// Common app modules
		'realize-debugging': 'lib/common/modules/debugging',
		'realize-sync': 'lib/common/modules/sync',
		'realize-mock-backend': 'lib/common/modules/mock-backend',
		'realize-lodash': 'lib/common/modules/lodash',

		// Common app models
		'widget': 'lib/common/models/widget',
		'user': 'lib/common/models/user',
		'screen': 'lib/common/models/screen',
		'view': 'lib/common/models/view',
		'context': 'lib/common/models/context',
		'plugin': 'lib/common/models/plugin',
		'util': 'lib/common/models/util',
		'notification': 'lib/common/models/notification',
		'error': 'lib/common/models/error',

		//Loader
		'bootstrap': 'bootstrap'
	},
	shim: {
		'angular': {'deps': ['jquery'], 'exports': 'angular'},
		'angular-ui-router': ['angular'],
		'angularMocks': {
			deps: ['angular'],
			'exports': 'angular.mock'
		},
		'angular-charts': {
			deps: ['jquery', 'angular', 'd3']
		},
		'ngTouch': {
			deps: ['angular'],
			exports: 'ngTouch'
		},
		'angular-ui-bootstrap': {
			deps: ['angular']
		},
		'html_templates_jsfied': {
			deps: ['angular']
		},
		'http-auth-interceptor': {
			deps: ['angular']
		},
		'angularAMD': {
			deps: ['angular']
		},
		'ngload': {
			deps: ['angularAMD']
		},
		'angular-formly': {
			deps: ['angular']
		},
		'ngRoute': {
			deps: ['angular']
		},
		'angular-growl': {
			deps: ['angular']
		},
		'angular-animate': {
			deps: ['angular']
		},
		'angular-gridster': {
			deps: ['angular', 'jquery-ui', 'es5-shim']
		},
		'angular-spinner': {
			deps: ['angular', 'spin']
		},
		'jquery-ui': {
			deps: ['jquery']
		},
        'angular-leaflet': {
            deps: ['angular', 'leaflet']
        }

	},
	priority: [
		"angular"
	],
	deps: [
		"bootstrap"
	],
	waitSeconds: 0
});
define(['app', 'angular', 'moment', 'angular-charts', 'view', 'context', 'realize-sync'], function (app, angular, moment) {
	app.register.controller('ChartCtrl', ['$scope', 'sync', 'user', 'EVENTS', 'view', 'context', function ($scope, sync, user, EVENTS, view, context) {
		$scope.hashkey = $scope.widgetData.hashkey;
		$scope.chartType = "line";

		$scope.render = function () {
			view.getDetail(context.getScopeName(), context.getScopeHash(), $scope.widgetData.settings.source.value)
			.then(function (data) {
				$scope.allChartData = data;
				$scope.chartConfig = {
					title: data.name,
					legend: {
						display: false,
						position: 'left'
					},
					labels: false,
					xAxisMaxTicks: 3
				};

				var series = [];
				var chartData = [];
				var i;
				for (i = 0; i < data.data.y.length; i++) {
					series.push(data.data.y[i].label);
				}

				for (i = 0; i < data.data.y[0].data.length; i++) {
					var y = [];
					var x = data.data.x.data[i];
					var m = moment(x).format("M/D/YY");
					for (var j = 0; j < data.data.y.length; j++) {
						y.push(data.data.y[j].data[i]);
					}
					chartData.push({
						x: m,
						y: y,
						tooltip: m
					});
				}


				$scope.chartData = {
					series: series,
					data: chartData
				};

				if (chartData.length > 0) {
					$scope.number = chartData[chartData.length - 1].y[0];
				} else {
					$scope.number = 0;
				}

				$scope.viewData = {
					"chart": {
						"chartData": $scope.chartData,
						"chartType": $scope.chartType,
						"chartConfig": $scope.chartConfig
					},
					"number": {
						"number": $scope.number
					}
				};
			});
		};

		$scope.$onRootScope(EVENTS.widgetSettingsChange, function (event, widgetKey) {
			console.log("Chart received settings change event", widgetKey);
			if (widgetKey === $scope.hashkey) {
				$scope.render();
			}
		});

		$scope.render();
	}]);
});


define(['app', 'angular', 'moment', 'view', 'context', 'user', 'realize-sync'], function (app, angular, moment) {
	app.register.controller('FormCtrl', ['$scope', 'sync', 'user', 'EVENTS', 'view', 'context', function ($scope, sync, user, EVENTS, view, context) {
		$scope.hashkey = $scope.widgetData.hashkey;
		$scope.formData = {};

		$scope.render = function () {
			view.getDetail(context.getScopeName(), context.getScopeHash(), $scope.widgetData.settings.source.value).then(function (data) {
				var fields = data.data.fields;
				$scope.formOptions = {
					"uniqueFormId": $scope.hashkey,
					"submitCopy": "Save"
				};

				var formFields = [];
				for (var i = 0; i < fields.length; i++) {
					var field = fields[i];
					var formField = {
						type: field.widget,
						label: field.description,
						name: field.name
					};

					formFields.push(formField);
				}
				$scope.formFields = formFields;

				$scope.viewData = {
					form: {
						formData: $scope.formData,
						formFields: $scope.formFields,
						formOptions: $scope.formOptions
					}
				};
			});
		};

		$scope.save = function () {
			console.log("Saving form with data", $scope.formData);
			var postData = {};
			for (var i = 0; i < $scope.formFields.length; i++) {
				postData[$scope.formFields[i].name] = $scope.formData[i];
			}

			view.saveData(context.getScopeName(), context.getScopeHash(), $scope.widgetData.settings.source.value, postData).then(function (data) {
				console.log("Form saved properly");
			});
		};
		// change settings when an ancestor widget broadcasts to do it.
		$scope.$onRootScope(EVENTS.widgetSettingsChange, function (event, widgetKey) {
			console.log("Chart received settings change event", widgetKey);
			if (widgetKey === $scope.hashkey) {
				$scope.render();
			}
		});

		$scope.render();

	}]);
});


define(['app', 'angular'], function (app, angular) {
	app.register.controller('IntroCtrl', ['$scope', function ($scope) {
		$scope.hashkey = $scope.widgetData.hashkey;

		$scope.viewData = {
			"long": {
				"text": "Welcome to your new dashboard!  Widgets are visual elements that can show you charts, text, maps, and anything else you could want (you can even make your own!).  Get started by clicking on 'add widget' above."
			},
			"short": {
				"text": "Welcome to your dashboard!  Click on 'add widgets' above to add a widget."
			}
		};
	}]);

});


define(['app', 'angular', 'moment', 'view', 'context', 'user', 'realize-sync'], function (app, angular, moment) {
	app.register.controller('MapCtrl', ['$scope', 'sync', 'user', 'EVENTS', 'view', 'context', function ($scope, sync, user, EVENTS, view, context) {
		$scope.hashkey = $scope.widgetData.hashkey;
		$scope.formData = {};

		$scope.render = function () {
			view.getDetail(context.getScopeName(), context.getScopeHash(), $scope.widgetData.settings.source.value).then(function (data) {


				$scope.viewData = {
					map: {

					}
				};
			});
		};

		// change settings when an ancestor widget broadcasts to do it.
		$scope.$onRootScope(EVENTS.widgetSettingsChange, function (event, widgetKey) {
			console.log("Chart received settings change event", widgetKey);
			if (widgetKey === $scope.hashkey) {
				$scope.render();
			}
		});

		$scope.render();

	}]);
});


define(['app', 'angular', 'user'], function (app, angular) {
	app.register.controller('IndexCtrl', ['$scope', 'user', 'EVENTS', function ($scope, user, EVENTS) {

		$scope.data = {};
		$scope.switch = function (type) {
			console.log('switchToLogin.clicked!');
			$scope.$emit(EVENTS.switchWidgetTree, type, 'default');
		};

		$scope.register = function () {
			user.loginOrRegister($scope.data, "register").then(function () {

			}).catch(function (err) {
				$scope.emailError = err.email;
				$scope.passwordError = err.password;
			});
		};

	}]);
});
define(['app', 'angularAMD', 'angular', 'jquery', 'angular-ui-bootstrap', 'realize-sync', 'widget', 'user', 'screen'], function (app, angularAMD, angular, $) {
	app.register.controller('WidgetDashboardCtrl', ['$scope', 'widget', 'widgetMeta', '$element', '$rootScope', 'sync', 'user', 'EVENTS', 'screen', '$modal', function ($scope, widget, widgetMeta, $element, $root, sync, user, EVENTS, screen, $modal) {
		$scope.hashkey = $scope.widgetData.hashkey;
		$scope.itemMap = {
			sizeX: 'widgetData.layout.sizeX',
			sizeY: 'widgetData.layout.sizeY',
			row: 'widgetData.layout.row',
			col: 'widgetData.layout.col'
    	};

		$scope.gridsterOpts = {
		  columns: 4, // the width of the grid, in columns
		  colWidth: 'auto', // can be an integer or 'auto'.  'auto' uses the pixel width of the element divided by 'columns'
		  rowHeight: 125, // can be an integer or 'match'.  Match uses the colWidth, giving you square widgets.
		  margins: [10, 10], // the pixel distance between each widget
		  defaultSizeX: 4, // the default width of a gridster item, if not specifed
      	  defaultSizeY: 2, // the default height of a gridster item, if not specifie
		  mobileBreakPoint: 600, // if the screen is not wider that this, remove the grid layout and stack the items
		  resize: {
			 enabled: false
		  },
		  draggable: {
			 enabled: true,
			 stop: function(event, uiWidget, $element) {
				 $scope.updateWidgetPositions();
			 }
		  }
		};

		console.log("Loaded dashboard widget", $scope.hashkey);
		$scope.type = "widgets";
		var modalInstance;

		$scope.updateWidgetPositions = function(){
			var hashkeys = [];
			for(var i = 0; i < $scope.loadedWidgets.length; i++){
				hashkeys.push({
					hashkey: $scope.loadedWidgets[i].hashkey,
					layout: $scope.loadedWidgets[i].layout
				});
			}
			widget.updateWidgetPositions(hashkeys);
		};

		$scope.open = function () {

			modalInstance = $modal.open({
				templateUrl: 'widgetModal.tpl.html',
				scope: $scope
			});
		};

		$scope.ok = function () {
			$modal.$close();
		};

		$scope.setupDashboard = function () {
			$scope.data = widget.listInstalledByParent($scope.hashkey).then(function (data) {
				$scope.loadedWidgets = data;
			});
		};

		$scope.add = function (widgetObj) {
			var timestamp = new Date().getTime();
			widgetObj.name = widgetObj.name + "_" + timestamp;
			widgetObj.parent = $scope.hashkey;

			console.log("Adding a widget to the dashboard: ", widgetObj);
			widget.create(widgetObj).then(function (data) {
				$scope.loadedWidgets.push(data);
			});
		};

		$scope.$onRootScope(EVENTS.widgetSettingsChange, function (event, widgetKey) {
			console.log("Dashboard received settings change event", widgetKey);
			if (widgetKey === $scope.hashkey) {
				$scope.setupDashboard();
			}
		});

		$scope.$onRootScope(EVENTS.widgetAddToDash, function (event, hashkey, widgetObj) {
			console.log("Dashboard received widget add event", hashkey);
			if (hashkey === $scope.hashkey) {
				$scope.add(widgetObj);
			}
		});

		$scope.$watch('loadedWidgets', function(newVal, oldVal){
			if(newVal !== undefined){
				$scope.gridsterOpts.minRows = newVal.length;
				$scope.gridsterOpts.maxRows = newVal.length;
			}
		});

		$scope.setupDashboard();
	}]);
});


define(['app', 'angular', 'user'], function (app, angular) {
	app.register.controller('IndexCtrl', ['$scope', 'user', 'EVENTS', function ($scope, user, EVENTS) {

		$scope.data = {};
		$scope.switch = function (type) {
			console.log('switchToLogin.clicked!');
			$scope.$emit(EVENTS.switchWidgetTree, type, 'default');
		};

		$scope.register = function () {
			user.loginOrRegister($scope.data, "register").then(function () {

			}).catch(function (err) {
				$scope.emailError = err.email;
				$scope.passwordError = err.password;
			});
		};

	}]);
});
define(['app', 'angular', 'user', 'realize-sync'], function (app, angular) {
	app.register.controller('LoginCtrl', ['$scope', '$q', '$window', 'user', 'sync', function ($scope, $q, $window, user, sync) {
		console.log('LoginCtrl scope', $scope);
		$scope.data = {};

		$scope.login = function () {
			user.loginOrRegister($scope.data, "login").then(function () {

			}).catch(function (err) {
				$scope.emailError = err.email;
				$scope.passwordError = err.password;
			});
		};
	}]);
});


define(['app', 'angular'], function (app, angular) {
	app.register.controller('RegisterCtrl', ['$scope', '$q', '$window', 'user', 'sync', function ($scope, $q, $window, user, sync) {
		console.log('RegisterCtrl scope', $scope);
		$scope.data = {};

		$scope.register = function () {
			user.loginOrRegister($scope.data, "register").then(function () {

			}).catch(function (err) {
				$scope.emailError = err.email;
				$scope.passwordError = err.password;
			});
		};
	}]);
});


define(['app', 'angular'], function (app, angular) {
	app.register.controller('RemovedCtrl', ['$scope', function ($scope) {
		$scope.hashkey = $scope.widgetData.hashkey;

		$scope.viewData = {
			"long": {
				"text": "This widget is currently unavailable.  Please contact your server administrator for more help."
			},
			"short": {
				"text": "Widget not available right now."
			}
		};
	}]);

});


})( window, window.angular );
