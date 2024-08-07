import { observable } from 'mobx';

class AxiosState {
	gaEvent = true
	ReactGA = null;
	generateRandomId = false;
	@observable sessionInfo = {
        lastSyncTime: null,
        apiObj: null
    }
	setGaEvent(gaEvent) {
		this.gaEvent = gaEvent;
	}
	getGaEvent() {
		return this.gaEvent;
	}
	getReactGA() {
		return this.ReactGA;
	}
	setReactGA(ReactGA) {
		this.ReactGA = ReactGA;
	}
	shouldGenerateRandomId() {
		return this.generateRandomId;
	}
	setRandomIdForNullId(randomIdForNullId) {
		this.generateRandomId = randomIdForNullId;
	}
}

const axiosState = new AxiosState();
export default axiosState;