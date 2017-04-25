
(function () {
  'use strict';

  angular.module('BlurAdmin.pages.changeRequest')
      .service('candidatePolicyService', candidatePolicyService);

  /** @ngInject */
  function candidatePolicyService($http, $location, $q) {

    var _candidatePolicy, _device, _profile, _match_criteria;

    this.retrieveCandiatePolicy = function() {
      return _candidatePolicy;
    }

    this.getDevice = function() {
      return _device;
    }

    this.getProfile = function() {
      return _profile;
    }

    this.getCandidatePolicy = function(device, profile, matchCriteria) {
      if (_candidatePolicy === undefined) {
        return $http({
          method : "POST",
          url : "/api/v1.0/oe/candidate_policy/",
          data: {
            device: {
              hostname: device.hostname
            },
            profile: {
              name: profile.name
            },
            match_criteria: matchCriteria
          }
        }).then(function mySuccess(response){
          console.log(response);
          _candidatePolicy = response.data.data;
          return _candidatePolicy;
        }, function myError(response) {
          console.log(response)
        });
      } else {
        return $q.resolve(_candidatePolicy);
      }
    };

    this.updateCandidatePolicy = function(new_cp) {
      _candidatePolicy = new_cp;
    }

    this.updateDevice = function(device) {
      _device = device;
    }

    this.updateProfile = function(profile) {
      _profile = profile;
    }

    this.updateMatchCriteria = function(mc) {
      _match_criteria = mc;
    }

    this.applyCandidatePolicy = function() {
      return $http({
          method : "POST",
          url : "/api/v1.0/oe/candidate_policy/apply/",
          data: {
            device: {
              hostname: device.hostname
            },
            profile: {
              name: profile.name
            },
            match_criteria: matchCriteria
          }
        }).then(function mySuccess(response){
          console.log(response);
          return true;
        }, function myError(response) {
          console.log(response)
          return false;
        });
    }


  }

})();
