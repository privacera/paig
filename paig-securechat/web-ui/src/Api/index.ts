import axios, { AxiosRequestConfig } from "axios";

// axios.defaults.baseURL = "/api/v1/";
// console.log("Base URL:", axios.defaults.baseURL);

axios.defaults.withCredentials = true

const fetchData = async (configuration: string | AxiosRequestConfig) => {
  let axiosConfig: AxiosRequestConfig = {};
  typeof configuration === "string" && (axiosConfig.url = configuration);

  if (typeof configuration !== "string") {
    if (configuration.headers) {
      axiosConfig.headers = {
        ...axiosConfig.headers,
        ...configuration.headers
      };
    }
    axiosConfig = {
      ...axiosConfig,
      ...configuration
    };
  }

  const config: AxiosRequestConfig = { ...axiosConfig };

  try {
    const resp = await axios(config);
    return resp;
  } catch (error) {
    let err: any = error;
    if (err && err.response && err.response.status == 401) {
      if (window.location.pathname != '/login') {
        window.location.href = '/login';
      }
    }
    throw error;
  }
};

export default fetchData;
