import axios from "axios";

export const myAxios = axios.create({
  baseURL: "http://localhost:8080",
  timeout: 10000,
  withCredentials: true,
});

// 添加请求拦截器
axios.interceptors.request.use(
  function (config) {
    // 在发送请求之前做些什么
    return config;
  },
  function (error) {
    // 对请求错误做些什么
    return Promise.reject(error);
  }
);

// 添加响应拦截器
axios.interceptors.response.use(
  function (response) {
    // 2xx 范围内的状态码都会触发该函数。
    // 对响应数据做点什么
    console.log(response);

    // const { data } = response;

    // console.log(data);
    // // 未登录
    // if (data.status === 40100) {
    //   if (
    //     !response.request.responseURL.includes("user/current") &&
    //     !window.location.pathname.includes("user/login") // 若原本页面就是登录页面
    //   ) {
    //     window.location.href = `/login?redirect=${window.location.href};`;
    //   }
    // }

    return response;
  },
  function (error) {
    // 超出 2xx 范围的状态码都会触发该函数。
    // 对响应错误做点什么
    return Promise.reject(error);
  }
);

export default {
  myAxios,
};
