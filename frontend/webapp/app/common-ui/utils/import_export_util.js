import {observable, computed, action, ObservableMap} from 'mobx';
import { keyBy } from 'lodash';

export default class ImportExportUtil {
    defaultState = {
        export: false,
        import: false
    };
    @observable state={
        export: false,
        import: false,
        selectedCheckbox: new ObservableMap(),
        totalCheckbox: -1
    };
    constructor() {
        this.reset();
    }
    @observable data=[];
    @action
    reset() {
        Object.assign(this.state, this.defaultState);
        this.resetSelectedCheckbox();
    }
    setData(data=[]) {
        this.data = data;
        this.setTotalCount(data.length)
    }
    getSelectedIdString() {
        // return Array.from(this.state.selectedCheckbox).join(",");
        return this.getSelectIdList().join(",");
    }
    getSelectIdList() {
        return Array.from(this.state.selectedCheckbox).map(arr => arr[0]);
    }
    getSelectedData(){
        const keyValueData = keyBy(this.data, 'id');
        const result = [];
        this.getSelectIdList().forEach(id => {
            if(keyValueData.hasOwnProperty(id)) {
                result.push(keyValueData[id]);
            }
        });
        return result;
    }
    @computed
    get selectedCount() {
        return this.state.selectedCheckbox.size;
    }
    @action
    enableExport() {
        this.state.export = true;
        this.state.import = false;
    }
    @action
    enableImport() {
        this.state.export = false;
        this.state.import = true;
        this.resetSelectedCheckbox();
    }
    @action
    cancelImportExport() {
        this.state.export = false;
        this.state.import = false;
    }
    @computed
    get isExport() {
        return this.state.export;
    }
    @computed
    get isImport() {
        return this.state.import;
    }
    @action
    setTotalCount(total) {
        this.state.totalCheckbox = total;
    }
    get isAllChecked() {
        return this.data.length && this.data.every(d => this.state.selectedCheckbox.has(parseInt(d.id)));
    }
    isSelected(id) {
        return this.state.selectedCheckbox.has(parseInt(id));
    }
    @action resetExport = () => {
        this.state.export = false;
        this.resetSelectedCheckbox();
    }
    @action resetImport = () => {
        this.state.import = false;
        this.resetSelectedCheckbox();
    }
    @action resetSelectedCheckbox = () => {
        this.state.selectedCheckbox.clear();
    }
    checkboxClick=(e, id, isSelectAll=false) => {
        if (!e) {
            return;
        }
        let isChecked = e.target.checked;
        if (isChecked) {
            this.checked(isChecked, id, isSelectAll);
        } else {
            this.unChecked(isChecked, id, isSelectAll);
        }
    }
    @action checked = (checked, id, isSelectAll) => {
        if (isSelectAll) {
            this.data.forEach(d => this.state.selectedCheckbox.set(parseInt(d.id)), true);
        } else {
            this.state.selectedCheckbox.set(parseInt(id), true);
        }
    }
    @action unChecked = (checked, id, isSelectAll) => {
        if (isSelectAll) {
            this.data.forEach(d => this.state.selectedCheckbox.delete(parseInt(d.id)));
        } else {
            this.state.selectedCheckbox.delete(parseInt(id));
        }
    }
    removeSelected = (id) => {
        this.state.selectedCheckbox.delete(parseInt(id));
    }
    setDefaultChecked = (newSelectedCheckbox) => {
        Object.assign(this.state, { selectedCheckbox : newSelectedCheckbox });
    }
}

export class ImportExportAllUtil extends ImportExportUtil {

    constructor(props) {
        super(props)

    }
    
    @observable isAllSelected = false;

    @action reset() {
        this.isAllSelected = false;
        Object.assign(this.state, this.defaultState);
        this.resetSelectedCheckbox();
    }

    setData(data=[], total = -1) {
        this.data = data;
        this.setTotalCount(total || data.length)
    }

    @computed
    get selectedCount() {
        return this.isAllSelected ? this.state.totalCheckbox : this.state.selectedCheckbox.size;
    }
    @action resetExport = () => {
        this.isAllSelected = false;
        this.state.export = false;
        this.resetSelectedCheckbox();
    }

    @computed
    get isAllChecked() {
        if (this.isAllSelected) {
            return true;
        }
        return this.data.length && this.data.every(d => this.state.selectedCheckbox.has(parseInt(d.id)))
    }

    @computed
    get allSelected() {
        return this.isAllSelected;
    }

    @action
    setIsAllSelected = () => {
        this.isAllSelected = true;
    }
}

export class ImportExportByAttrAllUtil extends ImportExportAllUtil {
    constructor(attr) {
        super();
        this.attrName = attr || 'type';
    }

    checkboxClick=(e, id, isSelectAll=false, attr) => {
        if (!e) {
            return;
        }
        let isChecked = e.target.checked;
        if (isChecked) {
            this.checked(isChecked, id, isSelectAll, attr);
        } else {
            this.unChecked(isChecked, id, isSelectAll, attr);
        }
    }

    @action checked = (checked, id, isSelectAll, attr) => {
        if (isSelectAll) {
            // this.resetSelectedCheckbox();
            this.data.forEach(d => {
                if (attr) {
                    d[this.attrName] === attr && this.state.selectedCheckbox.set(parseInt(d.id), true)
                    return
                }else{
                    this.state.selectedCheckbox.set(parseInt(d.id), true)
                }
            })
        } else {
            this.state.selectedCheckbox.set(parseInt(id), true);
        }
    }
    @action unChecked = (checked, id, isSelectAll, attr) => {
        if (isSelectAll) {
            this.data.forEach(d =>  {
                if (attr) {
                    d[this.attrName] === attr && this.state.selectedCheckbox.delete(parseInt(d.id));
                    return
                }else{
                    this.state.selectedCheckbox.delete(parseInt(d.id))
                }
            });
        } else {
            this.state.selectedCheckbox.delete(parseInt(id));
        }
    }

    isAllAttrChecked(attr) {
        if(this.isAllSelected) return true;
        const filterArray = attr ? this.data.filter(el => el[this.attrName] === attr) : this.data;
        return filterArray.length && filterArray.every(d => this.state.selectedCheckbox.has(parseInt(d.id)));
    }

    getAttrData(attr) {
        if (!attr) {
            return this.data
        }
        return this.data.filter(el => el[this.attrName] === attr);
    }
    getDataBySelectedAttr(attr, prevData) {
        const mergeData = Object.assign(this.data, prevData)
        const ids = this.getSelectIdList();
        const dataList = mergeData.filter(d => ids.includes(d.id))
        if (!attr) {
            return dataList;
        }
        return dataList.map(m => m[attr]);
    }
    setPreSelection(values) {
        values.forEach(val => {
            this.state.selectedCheckbox.set(val, true);
        })
    }
} 

export class importExportByAttrUtil extends ImportExportUtil {
    constructor(attr) {
        super();
        this.reset();
        this.attrName = attr || 'name';
    }
    isSelected(attr) {
        return this.state.selectedCheckbox.has(attr);
    }
    get isAllChecked() {
        return this.data.length && this.data.every(d => this.state.selectedCheckbox.has(d[this.attrName]));
    }
    checkboxClick=(e, attr, isSelectAll=false) => {
        if (!e) {
            return;
        }
        let isChecked = e.currentTarget.checked || e.target.checked;
        if (isChecked) {
            this.checked(isChecked, attr, isSelectAll);
        } else {
            this.unChecked(isChecked, attr, isSelectAll);
        }
    }
    @action checked = (checked, attr, isSelectAll) => {
        if (isSelectAll) {
            this.data.forEach(d => this.state.selectedCheckbox.set(d[this.attrName]), true);
        } else {
            this.state.selectedCheckbox.set(attr, true);
        }
    }
    @action unChecked = (checked, attr, isSelectAll) => {
        if (isSelectAll) {
            this.data.forEach(d => this.state.selectedCheckbox.delete(d[this.attrName]));
        } else {
            this.state.selectedCheckbox.delete(attr);
        }
    }
    removeSelected = attr => {
        this.state.selectedCheckbox.delete(attr);
    }
}

export class BulkImportExportByAttrAllUtil extends ImportExportAllUtil {
    constructor(attr) {
        super();
        this.attrName = attr || 'id';
    }
    @action clearCheckbox() {
        this.isAllSelected = false;
        this.resetSelectedCheckbox();
    }
    @computed
    get isAllChecked() {
        if (this.isAllSelected) {
            return true;
        }
        return this.data.every(d => this.state.selectedCheckbox.has(d.id))
    }
    isSelected(id) {
        return this.state.selectedCheckbox.has(id);
    }

    checkboxClick=(e, id, isSelectAll=false, attr) => {
        if (!e) {
            return;
        }
        let isChecked = e.target.checked;
        if (isChecked) {
            this.checked(isChecked, id, isSelectAll, attr);
        } else {
            this.unChecked(isChecked, id, isSelectAll, attr);
        }
    }
    @action checked = (checked, id, isSelectAll) => {
        if (isSelectAll) {
            this.data.forEach(d => this.state.selectedCheckbox.set(d.id), true);
        } else {
            this.state.selectedCheckbox.set(id, true);
        }
    }
    @action unChecked = (checked, id, isSelectAll) => {
        if (isSelectAll) {
            this.data.forEach(d => this.state.selectedCheckbox.delete(d.id));
        } else {
            this.state.selectedCheckbox.delete(id);
        }
    }
    isAllAttrChecked(attr) {
        if(this.isAllSelected) return true;
        const filterArray = attr ? this.data.filter(el => el[this.attrName] === attr) : this.data;
        return filterArray.length && filterArray.every(d => this.state.selectedCheckbox.has(d.id));
    }

    getAttrData(attr) {
        if (!attr) {
            return this.data
        }
        return this.data.filter(el => el[this.attrName] === attr);
    }
}