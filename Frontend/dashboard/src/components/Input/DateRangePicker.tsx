import React from 'react';
import { FormControl, FormLabel } from '@chakra-ui/react';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';

interface DateRangePickerProps {
    startDate: Date | null;
    endDate: Date | null;
    onStartDateChange: (date: Date | null) => void;
    onEndDateChange: (date: Date | null) => void;
}

const DateRangePicker: React.FC<DateRangePickerProps> = ({
    startDate,
    endDate,
    onStartDateChange,
    onEndDateChange,
}) => (
    <FormControl>
        <FormLabel htmlFor="startDate">Start Date</FormLabel>
        <DatePicker selected={startDate} onChange={onStartDateChange} />
        <FormLabel htmlFor="endDate" mt={4}>
            End Date
        </FormLabel>
        <DatePicker selected={endDate} onChange={onEndDateChange} />
    </FormControl>
);

export default DateRangePicker;
