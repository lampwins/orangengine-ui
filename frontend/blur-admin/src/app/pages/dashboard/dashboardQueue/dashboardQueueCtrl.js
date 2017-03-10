/**
 * @author v.lugovksy
 * created on 16.12.2015
 */
(function () {
  'use strict';

  angular.module('BlurAdmin.pages.dashboard')
      .controller('DashboardQueueCtrl', DashboardQueueCtrl);

  /** @ngInject */
  function DashboardQueueCtrl($scope, baConfig, $http, $auth) {

    $scope.transparent = baConfig.theme.blur;
    var dashboardColors = baConfig.colors.dashboard;
    var colors = [];
    for (var key in dashboardColors) {
      colors.push(dashboardColors[key]);
    }

    function getRandomColor() {
      var i = Math.floor(Math.random() * (colors.length - 1));
      return colors[i];
    }

    function getChangeRequests() {

      $http({
        method: 'GET',
        url: '/api/v1.0/change_requests/'
      }).then(function successCallback(response) {
          console.log(response)
        }, function errorCallback(response) {
          console.log(response)
        });
    }

    getChangeRequests()


  }
})();
