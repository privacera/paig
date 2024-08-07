import React, { useEffect, useState } from 'react';

const PENDO_GUIDE_NAME = {
  POLICY_PAGE_FEEDBACK: 'policy-page-feedback',
  DASHBOARD_TOUR: 'dashboard-tour',
  APPLICATION_DETAIL_TOUR: 'application-detail-tour'
}

const PendoInitializer = ({apiKey, host}) => {
  useEffect(() => {
    if (!host) {
        host = 'https://cdn.pendo.io';
    }
    host = new URL(host).origin;
    if (apiKey) {
      (function(apiKey){
          (function(p,e,n,d,o){var v,w,x,y,z;o=p[d]=p[d]||{};o._q=o._q||[];
          v=['initialize','identify','updateOptions','pageLoad','track'];for(w=0,x=v.length;w<x;++w)(function(m){
              o[m]=o[m]||function(){o._q[m===v[0]?'unshift':'push']([m].concat([].slice.call(arguments,0)));};})(v[w]);
              y=e.createElement(n);y.async=!0;y.src=host+'/agent/static/'+apiKey+'/pendo.js';
              z=e.getElementsByTagName(n)[0];z.parentNode.insertBefore(y,z);})(window,document,'script','pendo');
      })(apiKey);
    }
  }, [apiKey, host]);

  return null;
};

let guideNameTimeoutIdMap = {}
const findActiveGuideByName = (name='', maxAttempts = 100) => {
  if (guideNameTimeoutIdMap[name]) {
    clearGuideTimeout(name);
  }
  const checkGuide = (attemptCount = 0) => {
    if (attemptCount >= maxAttempts) {
      return Promise.resolve(null);
    }

    let guide = null;
    if (window.pendo && window.pendo.getActiveGuides) {
      guide = window.pendo.getActiveGuides()?.find(g => g.name == name);
    }

    if (guide) {
      return Promise.resolve(guide);
    } else {
      return new Promise((resolve) => {
        let id = setTimeout(() => resolve(checkGuide(attemptCount + 1)), 1000);
        guideNameTimeoutIdMap[name] = id
      });
    }
  };

  return checkGuide();
}

const clearGuideTimeout = (name) => {
  clearTimeout(guideNameTimeoutIdMap[name]);
  delete guideNameTimeoutIdMap[name];
}

const triggerPendoFeedbackGuideManual = (name) => {
  let guide = window.pendo?.getActiveGuides()?.find(g => g.name === name);
  if (guide && !guide.isExpired() && !guide.isBeforeStartTime() && guide.launchMethod == 'api' && !guide.isGuideSnoozed() && !guide.isComplete()) {
    window.pendo.showGuideById(guide.id);
  }
}

export default PendoInitializer;
export {
  PENDO_GUIDE_NAME,
  findActiveGuideByName,
  clearGuideTimeout,
  triggerPendoFeedbackGuideManual
}