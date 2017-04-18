(function () {
  'use strict';

  angular.module('BlurAdmin.pages.changeRequest.tag', [])
    .config(routeConfig);

  /** @ngInject */
  function routeConfig($stateProvider) {
    $stateProvider
      .state('changeRequest.tag', {
        url: '/:id/tag',
        templateUrl: 'app/pages/changeRequest/tag/tag.html',
          title: 'Tag',
          controller: "TagCtrl"
      });
  }
})();
