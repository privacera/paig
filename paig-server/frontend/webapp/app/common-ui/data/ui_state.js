
class UiState {
	isCloud = true;
	isCloudEnv() {
		return this.isCloud;
	}
	setIsCloudEnv(cloudEnv) {
		this.isCloud = cloudEnv;
	}
}

let singleton = new UiState();
export default singleton;