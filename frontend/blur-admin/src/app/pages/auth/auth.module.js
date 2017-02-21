
(function () {
  'use strict';

  angular.module('BlurAdmin.pages')
  .controller('authLoginCtrl', function($scope, $auth, $rootScope, $window, $location) {

    $scope.login = function() {

      var user = {
        email: $scope.email,
        password: $scope.password
      };

      $auth.setBaseUrl('http://localhost:5000/');

      $auth.login(user)
        .then(function(response) {
          console.log(response);
          $window.localStorage.currentUser = JSON.stringify(response.data.user);
          $rootScope.currentUser = JSON.parse(localStorage.getItem('currentUser'));
          $location.path('/dashboard');
        })
        .catch(function(response) {
          console.log(response);
        });
    };

  });

})();