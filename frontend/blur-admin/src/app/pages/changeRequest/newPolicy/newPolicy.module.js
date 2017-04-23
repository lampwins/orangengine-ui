(function () {
  'use strict';

  angular.module('BlurAdmin.pages.changeRequest.newPolicy', ['satellizer', 'ui.select', 'ngSanitize'])
    .config(routeConfig);

  /** @ngInject */
  function routeConfig($stateProvider) {
    $stateProvider
      .state('changeRequest.newPolicy', {
        url: '/:id/newPolicy',
        templateUrl: 'app/pages/changeRequest/newPolicy/newPolicy.html',
        title: 'New Policy',
        //controller: "NewPolicyCtrl as vms"
      });
  }
})();
