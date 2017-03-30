/**
 * @author v.lugovsky
 * created on 16.12.2015
 */
(function () {
  'use strict';

  angular.module('BlurAdmin.pages', [
    'ui.router',
    'satellizer',

    'BlurAdmin.pages.dashboard',
    'BlurAdmin.pages.profile',
    'BlurAdmin.pages.login',
    'BlurAdmin.pages.devices',
    'BlurAdmin.pages.changeRequest'
  ])
      .config(routeConfig).run(runConfig);

  /** @ngInject */
  function routeConfig($stateProvider, $urlRouterProvider, baSidebarServiceProvider,
                       $authProvider) {

    $urlRouterProvider.otherwise('/dashboard');

    baSidebarServiceProvider.addStaticItem({
      title: 'Devices',
      icon: 'ion-fireball',
      stateRef: 'devices.list'
    });

  };

  function runConfig($rootScope, $location, $auth) {

    var routesThatDontRequireAuth = ['login'];

    $rootScope.$on('$stateChangeStart', function (ev, to, toParams, from, fromParams) {
      // if route requires auth and user is not logged in
      if (!routesThatDontRequireAuth.includes(to.title) && !$auth.isAuthenticated()) {
        // redirect back to login
        $location.path('/login');
      }
    });
  };

})();
