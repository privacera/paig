import CryptoJS from "crypto-js";

export const encryptData = (data: string): string => {
  const encryptedData: string = CryptoJS.AES.encrypt(data, "050cf42ee14d597188b0695a94df5e866d7eda5d06af32ff3ac329ddbcf7ca8a").toString();
  return encryptedData;
};

export const decryptData = (encryptedData: string): string => {
  const decryptedData: string = CryptoJS.AES.decrypt(encryptedData, "050cf42ee14d597188b0695a94df5e866d7eda5d06af32ff3ac329ddbcf7ca8a").toString(CryptoJS.enc.Utf8);
  return decryptedData;
};

export const SECURECHAT_BASE_ROUTE = "/securechat/api/v1";