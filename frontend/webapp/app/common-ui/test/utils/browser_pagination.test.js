import BrowserPagination from 'common-ui/utils/browser_pagination';

const apiData = [
    { "id": 1, "data": "data-1" }, { "id": 2, "data": "data-2" }, { "id": 3, "data": "data-3" }, { "id": 4, "data": "data-4" },
    { "id": 5, "data": "data-5" },{ "id": 6, "data": "data-6" }, { "id": 7, "data": "data-7" }, { "id": 8, "data": "data-8" },
    { "id": 9, "data": "data-9" }, { "id": 10, "data": "data-10" }, { "id": 11, "data": "data-11" }, { "id": 12, "data": "data-12" },
    { "id": 13, "data": "data-13" }, { "id": 14, "data": "data-14" }, { "id": 15, "data": "data-15" }, { "id": 16, "data": "data-16" },
    { "id": 17, "data": "data-17" }, { "id": 18, "data": "data-18" }, { "id": 19, "data": "data-19" }, { "id": 20, "data": "data-20" },
    { "id": 21, "data": "data-21" }
];

describe('Tests of browser pagination', () => {
    test('should have paginated data with page number = 0 and page size = 15', () => {
        const browserPagination = new BrowserPagination();
        const { data, pageState } = browserPagination.setData(apiData);

        expect(data.length).toEqual(15);
        expect(pageState.size).toEqual(15);
        expect(pageState.number).toEqual(0);
        expect(pageState.totalElements).toEqual(apiData.length);
        expect(pageState.totalPages).toEqual(Math.ceil(apiData.length / 15));
    });

    test('should change to page number = 1 with page size = 15', () => {
        const browserPagination = new BrowserPagination();
        browserPagination.setData(apiData);
        const { data, pageState } = browserPagination.changePageNumber(1);

        expect(data.length).toEqual(6);
        expect(pageState.size).toEqual(15);
        expect(pageState.number).toEqual(1);
        expect(pageState.totalElements).toEqual(apiData.length);
        expect(pageState.totalPages).toEqual(Math.ceil(apiData.length / 15));
    });

    test('should change to page number = 0 with page size = 50', () => {
        const browserPagination = new BrowserPagination();
        browserPagination.setData(apiData);
        const { data, pageState } = browserPagination.changePageSize(50);

        expect(data.length).toEqual(21);
        expect(pageState.size).toEqual(50);
        expect(pageState.number).toEqual(0);
        expect(pageState.totalElements).toEqual(apiData.length);
        expect(pageState.totalPages).toEqual(Math.ceil(apiData.length / 50));
    });

    test('should change to page number = 1 with page size = 50 and have no data', () => {
        const browserPagination = new BrowserPagination();
        browserPagination.setData(apiData);
        browserPagination.changePageSize(50);
        const { data, pageState } = browserPagination.changePageNumber(1);

        expect(data.length).toEqual(0);
        expect(pageState.size).toEqual(50);
        expect(pageState.number).toEqual(1);
        expect(pageState.totalElements).toEqual(apiData.length);
        expect(pageState.totalPages).toEqual(Math.ceil(apiData.length / 50));
    });

    test('should change to page number = -1 with page size = 15 and have no data', () => {
        const browserPagination = new BrowserPagination();
        browserPagination.setData(apiData);
        const { data, pageState } = browserPagination.changePageNumber(-1);

        expect(data.length).toEqual(0);
        expect(pageState.size).toEqual(15);
        expect(pageState.number).toEqual(-1);
        expect(pageState.totalElements).toEqual(apiData.length);
        expect(pageState.totalPages).toEqual(Math.ceil(apiData.length / 15));
    });

    test('should change to page number = 10 with page size = 15 and have no data', () => {
        const browserPagination = new BrowserPagination();
        browserPagination.setData(apiData);
        const { data, pageState } = browserPagination.changePageNumber(10);

        expect(data.length).toEqual(0);
        expect(pageState.size).toEqual(15);
        expect(pageState.number).toEqual(10);
        expect(pageState.totalElements).toEqual(apiData.length);
        expect(pageState.totalPages).toEqual(Math.ceil(apiData.length / 15));
    });

    test('should change to page number = 0 with page size = 0 and have no data', () => {
        const browserPagination = new BrowserPagination();
        browserPagination.setData(apiData);
        const { data, pageState } = browserPagination.changePageSize(0);

        expect(data.length).toEqual(0);
        expect(pageState.size).toEqual(0);
        expect(pageState.number).toEqual(0);
        expect(pageState.totalElements).toEqual(apiData.length);
        expect(pageState.totalPages).toEqual(0);
    });

    test('should change to page number = 0 with page size = -1 and have no data', () => {
        const browserPagination = new BrowserPagination();
        browserPagination.setData(apiData);
        const { data, pageState } = browserPagination.changePageSize(-1);

        expect(data.length).toEqual(0);
        expect(pageState.size).toEqual(-1);
        expect(pageState.number).toEqual(0);
        expect(pageState.totalElements).toEqual(apiData.length);
        expect(pageState.totalPages).toEqual(0);
    });
});