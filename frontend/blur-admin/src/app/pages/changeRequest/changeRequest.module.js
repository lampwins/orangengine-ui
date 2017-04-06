
(function () {
  'use strict';

  angular.module('BlurAdmin.pages.changeRequest', [
    'BlurAdmin.pages.changeRequest.summary',
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
