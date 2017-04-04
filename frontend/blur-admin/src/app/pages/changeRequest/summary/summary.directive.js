/**
 * @author v.lugovksy
 * created on 16.12.2015
 */
(function () {
  'use strict';

  angular.module('BlurAdmin.pages.changeRequest')
      .directive('summary', summary);

  /** @ngInject */
  function dashboardQueue() {
    return {
      restrict: 'EA',
      controller: 'SummaryCtrl',
      templateUrl: 'app/pages/changeRequest/summary/summary.html'
    };
  }
})();
