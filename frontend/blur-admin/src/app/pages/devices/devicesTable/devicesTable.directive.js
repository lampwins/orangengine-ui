/**
 * @author v.lugovksy
 * created on 16.12.2015
 */
(function () {
  'use strict';

  angular.module('BlurAdmin.pages.devices')
      .directive('devicesTable', devicesTable);

  /** @ngInject */
  function devicesTable() {
    return {
      restrict: 'EA',
      controller: 'DevicesTableCtrl',
      templateUrl: 'app/pages/devices/devicesTable/devicesTable.html'
    };
  }
})();
