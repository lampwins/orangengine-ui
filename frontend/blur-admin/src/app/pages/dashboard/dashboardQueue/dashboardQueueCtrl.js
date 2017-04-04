/**
 * @author v.lugovksy
 * created on 16.12.2015
 */
(function () {
  'use strict';

  angular.module('BlurAdmin.pages.dashboard')
      .controller('DashboardQueueCtrl', DashboardQueueCtrl);


  /** @ngInject */
  function DashboardQueueCtrl($scope, baConfig, $http, $auth, $location) {


    $http({
      method : "GET",
      url : "/api/v1.0/change_requests/"
    }).then(function mySuccess(response){
      console.log(response)
      $scope.queueData = response.data.data;
    }, function myError(response) {
      console.log(response)
      $scope.name = response.statusText;
    });

    $scope.go = function(path) {
      $location.path(path);
    };


}
})();
