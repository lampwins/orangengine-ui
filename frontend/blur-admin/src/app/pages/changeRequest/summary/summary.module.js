(function () {
  'use strict';

  angular.module('BlurAdmin.pages.changeRequest.summary', [])
    .config(routeConfig);

  /** @ngInject */
  function routeConfig($stateProvider) {
    $stateProvider
      .state('changeRequest.summary', {
        url: '/:id/summary',
        templateUrl: 'app/pages/changeRequest/summary/summary.html',
        title: 'Summary',
        controller: "SummaryCtrl"
      });
  }
})();
