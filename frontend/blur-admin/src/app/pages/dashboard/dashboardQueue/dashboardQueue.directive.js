/**
 * @author v.lugovksy
 * created on 16.12.2015
 */
(function () {
  'use strict';

  angular.module('BlurAdmin.pages.dashboard')
      .directive('dashboardQueue', dashboardQueue);

  /** @ngInject */
  function dashboardQueue() {
    return {
      restrict: 'EA',
      controller: 'DashboardQueueCtrl',
      templateUrl: 'app/pages/dashboard/dashboardQueue/dashboardQueue.html'
    };
  }
})();
