(function () {
  'use strict';

  angular.module('BlurAdmin.pages.changeRequest.done', [])
    .config(routeConfig);

  /** @ngInject */
  function routeConfig($stateProvider) {
    $stateProvider
      .state('changeRequest.done', {
        url: '/:id/done',
        templateUrl: 'app/pages/changeRequest/done/done.html',
          title: 'Done',
          controller: "DoneCtrl"
      });
  }
})();
