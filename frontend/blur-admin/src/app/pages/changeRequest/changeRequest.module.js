
(function () {
  'use strict';

  angular.module('BlurAdmin.pages.changeRequest', [
    'BlurAdmin.pages.changeRequest.summary',
    'BlurAdmin.pages.changeRequest.environment',
    'BlurAdmin.pages.changeRequest.append',
    'BlurAdmin.pages.changeRequest.tag',
    'BlurAdmin.pages.changeRequest.newPolicy',
    'BlurAdmin.pages.changeRequest.confirm',
    'satellizer'
  ])
      .config(routeConfig);

  /** @ngInject */
  function routeConfig($stateProvider) {
    $stateProvider
        .state('changeRequest', {
          url: '/changeRequest',
          template: '<ui-view  autoscroll="true" autoscroll-body-top></ui-view>',
          abstract: true,
          title: 'Change Request',
        });


  }

})();
