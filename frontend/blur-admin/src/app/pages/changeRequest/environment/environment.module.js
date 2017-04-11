(function () {
  'use strict';

  angular.module('BlurAdmin.pages.changeRequest.environment', [])
    .config(routeConfig);

  /** @ngInject */
  function routeConfig($stateProvider) {
    $stateProvider
      .state('changeRequest.environment', {
        url: '/:id/environment',
        templateUrl: 'app/pages/changeRequest/environment/environment.html',
          title: 'Environment',
          controller: "EnvironmentCtrl"
      });
  }
})();
