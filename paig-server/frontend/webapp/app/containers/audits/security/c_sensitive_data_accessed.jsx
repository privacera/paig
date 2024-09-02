import React, { Component, Fragment} from 'react';
import {inject} from 'mobx-react';
import {ObservableMap} from 'mobx';
import { isEmpty } from 'lodash';

import f from 'common-ui/utils/f';
import {Utils} from 'common-ui/utils/utils';
import { Loader, getSkeleton } from 'common-ui/components/generic_components'
import VSensitiveDataAccessed from 'components/audits/security/v_sensitive_data_accessed';

@inject('encryptDecryptStore', 'securityAuditsStore', 'aiPoliciesStore', 'vectorDBPolicyStore')
class CSensitiveDataAccessed extends Component {
    constructor(props) {
        super(props);

        this.state={
            loading: true,
            data : [],
            accessPolicyId: null
        }
    }
    policyIdPolicyMap = new ObservableMap();
    vectorDBPolicyIdPolicyMap = new ObservableMap();
    componentDidMount() {
        this.fetchAccessPolicy();
    }
    capitalizeFirstLetter = (str) => {
        return str.charAt(0).toUpperCase() + str.slice(1);
    };
    highlightWordsInBrackets = (text) => {
        const pattern = /(<<[^<<>>]+>>)/g;
        const parts = text.split(pattern);

        return parts.map((part, index) => {
          if (part.match(pattern)) {
            return <span key={index} style={{ fontWeight: 'bold', color: 'red' }}>{part}</span>;
          } else {
            return <Fragment key={index}>{part}</Fragment>;
          }
        });
    }
    getDecryptDataList = async (data) => {
        let res = await this.props.encryptDecryptStore.decrypt(data);
        if (res.decryptedDataList) {
            return res.decryptedDataList.map(decryptedData => Utils.decodeBase64(decryptedData));
        } else if (res.decryptedData) {
            return [Utils.decodeBase64(res.decryptedData)];
        } else {
            return [];
        }
    }
    scrollOnActiveAccordion = (attrName, scrollableContainer) => {
        const selector = document.querySelector(`#${attrName}`);
        if (selector && scrollableContainer) {
            const newPosition = selector.getBoundingClientRect().top - scrollableContainer.getBoundingClientRect().top - 50;
            scrollableContainer.scrollTo({
                top: newPosition,
                behavior: 'smooth',
            });
        }   
    };    
    fetchSensitiveData = async () => {
        const {selectedModel} = this.props;
        const { accessPolicyId } = this.state;
        let models = []
        let queryParams = {
            sort: 'eventTime,threadSequenceNumber,desc',
            'includeQuery.threadId': selectedModel?.threadId
        }

        let aiPolicyIds = new Set();
        let vectorDBPolicies = new Set();
        let vectorDbId = null;

        if (!isEmpty(selectedModel)) {
            try {
                let response = await this.props.securityAuditsStore.fetchSecurityAudits({ params:queryParams });
                models = response.models.reverse();
                let encryptedDataList = [];
                for (let model of models) {
                    const modelMessages = model.messages || []
                    for (let message of modelMessages) {
                        if (message.originalMessage) {
                            encryptedDataList.push(message.originalMessage);
                        }
                        if (message.maskedMessage) {
                            encryptedDataList.push(message.maskedMessage);
                        }
                        if (model.paigPolicyIds) {
                            // Filter out configId from paigPolicyIds
                            model.paigPolicyIds = model.paigPolicyIds.filter(id => Number(id) !== accessPolicyId);
                            // Collect AI Policy IDs excluding configId
                            model.paigPolicyIds.forEach(id => {
                                aiPolicyIds.add(Number(id));
                            });
                        }
                        if (model.context?.vectorDBInfo?.vectorDBPolicyInfo) {
                            vectorDbId = model.context.vectorDBInfo.vectorDBId;
                            model.context.vectorDBInfo.vectorDBPolicyInfo.forEach(policy => {
                                vectorDBPolicies.add(Number(policy.id));
                            });
                        }
                    }
                }    
                let decryptedDataResponse = await this.getDecryptDataList({
                    encryptionKeyId: selectedModel.encryptionKeyId,
                    encryptedDataList: encryptedDataList
                });
                let decryptedDataIndex = 0;
                for (let model of models) {
                    const modelMessages = model.messages || [];
                        for (let message of modelMessages) {
                        if (message.originalMessage) {
                            message.decryptedMessage = decryptedDataResponse[decryptedDataIndex];
                            decryptedDataIndex++;
                        }
                        if (message.maskedMessage) {
                            message.decryptedMaskedMessage = decryptedDataResponse[decryptedDataIndex];
                            decryptedDataIndex++;
                        }
                    }
                }

                // Fetch AI Policies, adding a delay as rendering is happening after the data is fetched sometimes
                setTimeout(() => {
                    this.fetchAiPolicies(Array.from(aiPolicyIds), vectorDbId, Array.from(vectorDBPolicies));
                }, 1000);
            } catch (e) {
                f.handleError()(e);
            }
        }
        this.setState({data:models, loading: false}, () => {
            this.scrollOnActiveAccordion('selectedRow', document.querySelector('[data-testid="modal-body"]'))
        });
    }
    fetchAccessPolicy = async () => {
        const {selectedModel, applicationKeyMap} = this.props;
        let app = applicationKeyMap[selectedModel.applicationKey];
        try {
            let response = await this.props.aiPoliciesStore.getGlobalPermissionPolicy(app.id);
            this.setState({ accessPolicyId: response.id});
        } catch (e) {
            console.error('Failed to get policy count', e);
        } finally {
            this.fetchSensitiveData();
        }
    }
    fetchAiPolicies = async(ids, vectorDbId, vectorDBPoliciesIds) => {
        const {selectedModel, applicationKeyMap} = this.props;
        let app = applicationKeyMap[selectedModel.applicationKey];

        for (let id of ids) {
            try {
                let policy = await this.props.aiPoliciesStore.getPolicyById(app.id, id);
                this.policyIdPolicyMap.set(id, policy);
            } catch(e) {
                this.policyIdPolicyMap.set(id, null);
            }
        }

        if (vectorDbId) {
            for (let id of vectorDBPoliciesIds) {
                try {
                    let policy = await this.props.vectorDBPolicyStore.getPolicyById(vectorDbId, id);
                    this.vectorDBPolicyIdPolicyMap.set(id, policy);
                } catch(e) {
                    this.vectorDBPolicyIdPolicyMap.set(id, null);
                }
            }
        }
    }
    render() {
        const {selectedModel} = this.props;
        const {data, loading} = this.state;

        return (
            <Loader loaderContent={getSkeleton('TWO_SLIM_LOADER3')} isLoading={loading} >
                <VSensitiveDataAccessed
                    selectedModel={selectedModel}
                    highlightWordsInBrackets={this.highlightWordsInBrackets}
                    capitalizeFirstLetter={this.capitalizeFirstLetter}
                    data={data}
                    policyIdPolicyMap={this.policyIdPolicyMap}
                    vectorDBPolicyIdPolicyMap={this.vectorDBPolicyIdPolicyMap}
                />
            </Loader>
        )
    }
}

export default CSensitiveDataAccessed;