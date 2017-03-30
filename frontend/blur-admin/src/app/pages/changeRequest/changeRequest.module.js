(function () {
  'use strict';

  angular.module('BlurAdmin.pages.changeRequest', [
    'satellizer',
    'BlurAdmin.pages.changeRequest.form',
    ]).config(routeConfig);

  /** @ngInject */
  function routeConfig($stateProvider) {
    $stateProvider
        .state('changeRequest', {
          url: '/changeRequest',
          template : '<ui-view  autoscroll="true" autoscroll-body-top></ui-view>',
          abstract: true
        });
  }

})();