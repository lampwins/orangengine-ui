(function () {
  'use strict';

  angular.module('BlurAdmin.pages.changeRequest.append', [])
    .config(routeConfig);

  /** @ngInject */
  function routeConfig($stateProvider) {
    $stateProvider
      .state('changeRequest.append', {
        url: '/:id/append',
        templateUrl: 'app/pages/changeRequest/append/append.html',
          title: 'Append',
          controller: "AppendCtrl"
      });
  }
})();
