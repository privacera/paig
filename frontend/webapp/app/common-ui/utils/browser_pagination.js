import { DEFAULTS } from 'common-ui/utils/globals';

export default class BrowserPagination {

    data = [];

    constructor() {
        this.pageNumber = 0;
        this.pageSize = DEFAULTS.DEFAULT_PAGE_SIZE;
    }

    getAllData = () => {
        return this.data;
    }

    setData = (data = []) => {
        this.data = data;
        return this.applyPagination();
    }

    getPageState = () => {
        const totalElements = this.data.length;
        this.pageState = {
            number: this.pageNumber,
            size: this.pageSize ?? DEFAULTS.DEFAULT_PAGE_SIZE,
            totalPages: 0,
            totalElements: 0,
            numberOfElements: 0
        }
        this.pageState.totalElements = totalElements;
        this.pageState.numberOfElements = totalElements;
        this.pageState.totalPages = this.pageState.size > 0 ? Math.ceil(totalElements / this.pageState.size) : 0;

        return this.pageState;
    }

    setPageNumber = (pageNumber) => {
        this.pageNumber = pageNumber;
    }

    setPageSize = (pageSize = DEFAULTS.DEFAULT_PAGE_SIZE) => {
        this.pageSize = pageSize;
    }

    setStartEndIndex = () => {
        this.startIndex = this.pageNumber * this.pageSize;
        this.endIndex = this.startIndex + this.pageSize;
    }

    changePageNumber = (pageNumber = 0) => {
        this.setPageNumber(pageNumber);
        return this.applyPagination();
    }

    changePageSize = (pageSize = DEFAULTS.DEFAULT_PAGE_SIZE) => {
        this.setPageNumber(0);
        this.setPageSize(pageSize);
        return this.applyPagination();
    }

    applyPagination = () => {
        this.setStartEndIndex();

        return {
            data: this.pageSize > 0 ? this.data.slice(this.startIndex, this.endIndex) : [],
            pageState: this.getPageState()
        }
    }
}