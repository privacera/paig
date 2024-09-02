var DashboardUtils = {};

DashboardUtils.formatSensitiveDataInApplications = (data = {}) => {
    const transformedData = [];

    if (!data.traits) {
      return transformedData;
    }

    for (const key in data.traits) {
      const trait = {
        tag: key,
        queries: data.traits[key].count,
        graphData: []
      };

      if (data.traits[key].applicationName) {
        for (const appKey in data.traits[key].applicationName) {
          trait.graphData.push({
            name: appKey,
            data: [data.traits[key].applicationName[appKey].count],
          });
        }
      }

      transformedData.push(trait);
    }
    return transformedData;
  }

  export default DashboardUtils;