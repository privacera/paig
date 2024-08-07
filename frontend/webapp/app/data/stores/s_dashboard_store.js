import BaseStore from "./base_store";
import VDashboard from "../models/m_dashboard";

class DashboardStore extends BaseStore {
  constructor() {
    super({
      type: "Dashboard",
      baseUrl: "data-service/api/shield_audits"
    });
  }
  fetchCounts(opts = {}) {
    opts.path = "count";
    opts.recordMapper = (json) => new VDashboard(json);

    return this.fetch("", opts);
  }
  fetchUsageCounts(opts = {}) {
    opts.path = "usage_counts";
    opts.recordMapper = (json) => new VDashboard(json);

    return this.fetch("", opts);
  }
  fetchAccessDataCounts(opts = {}) {
    opts.path = "access_data_counts";
    opts.recordMapper = (json) => new VDashboard(json);
    return this.fetch("", opts);
  }

  fetchTraitCounts(opts = {}) {
    opts.path = "trait_counts";
    opts.recordMapper = (json) => new VDashboard(json);

    return this.fetch("", opts);
  }
  fetchUserIdCounts(opts = {}) {
    opts.path = "user_id_counts";
    opts.recordMapper = (json) => new VDashboard(json);

    return this.fetch("", opts);
  }
  fetchAppNameCounts(opts = {}) {
    opts.path = "app_name_counts";
    opts.recordMapper = (json) => new VDashboard(json);

    return this.fetch("", opts);
  }
  fetchAppNameByUserIdCounts(opts = {}) {
    opts.path = "app_by_user_counts";
    opts.recordMapper = (json) => new VDashboard(json);

    return this.fetch("", opts);
  }
  fetchTopUserIdCounts(opts = {}) {
    opts.path = "top_users_count";
    opts.recordMapper = (json) => new VDashboard(json);
    return this.fetch("", opts);
  }
  fetchUniqUserIdCounts(opts = {}) {
    opts.path = "uniq_user_id_counts";
    opts.recordMapper = (json) => new VDashboard(json);

    return this.fetch("", opts);
  }
  fetchUniqTraitCounts(opts = {}) {
    opts.path = "uniq_trait_counts";
    opts.recordMapper = (json) => new VDashboard(json);

    return this.fetch("", opts);
  }
  fetchActivityTrendCounts(opts = {}) {
    opts.path = "activity_trend_counts";
    opts.recordMapper = (json) => new VDashboard(json);

    return this.fetch("", opts);
  }
}

const dashboardStore = new DashboardStore();
export default dashboardStore;
