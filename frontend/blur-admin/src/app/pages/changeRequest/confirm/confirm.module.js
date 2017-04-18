(function () {
  'use strict';

  angular.module('BlurAdmin.pages.changeRequest.confirm', [])
    .config(routeConfig);

  /** @ngInject */
  function routeConfig($stateProvider) {
    $stateProvider
      .state('changeRequest.confirm', {
        url: '/:id/confirm',
        templateUrl: 'app/pages/changeRequest/confirm/confirm.html',
          title: 'Confirm',
          controller: "ConfirmCtrl"
      });
  }
})();
