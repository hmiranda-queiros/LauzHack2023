export default (tripType) => {
    switch (tripType) {
        case 'BIKE':
            return 'rgba(0, 155, 70, 1)';
        case 'CAR':
            return 'rgba(0, 1, 245,1)';
        case 'FOOT':
            return 'rgba(200, 200, 200, 1)';
        case 'TRANSFER':
            return 'rgba(0, 255, 255, 1)';
        case 'BUS':
        case 'METRO':
        case 'TRAIN':
        default:
            return 'rgba(0, 0, 0, 1)';
    }
}