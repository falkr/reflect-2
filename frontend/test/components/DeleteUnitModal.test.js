/* eslint-disable no-undef */
import { fireEvent, render, screen } from '@testing-library/svelte';
import DeleteUnitModal from '../../src/lib/components/DeleteUnitModal.svelte';
import { mockData } from '../../__mocks__/Data';

describe('DeleteUnitModal', () => {
	test('The delete unit button is rendered', () => {
		//Render as student
		render(DeleteUnitModal, { data: mockData[1] });

		//Check that the decline unit button is rendered when clicking the delete unit button
		expect(screen.getByText(/Delete Unit/i)).toBeInTheDocument();
	});
	test('The deleteUnitModal is rendered when clicking "delete unit" button', async () => {
		render(DeleteUnitModal, { data: mockData[1] });

		//Click the delete unit button
		const deleteBtn = screen.getByText(/Delete Unit/i);
		await fireEvent.click(deleteBtn);

		//Set the expected modal text after clicking the delete unit button
		const modalText =
			/Are you sure you want to delete this unit\? All the unit data will be deleted permanently/i;

		expect(screen.getByText(modalText)).toBeInTheDocument();
	});
	test('The deleteUnitModal is removed when clicking cancel', async () => {
		render(DeleteUnitModal, { data: mockData[1] });

		//Click the delete unit button to render the modal
		const deleteBtn = screen.getByText(/Delete Unit/i);
		await fireEvent.click(deleteBtn);
		const modalText = screen.getByText(
			/Are you sure you want to delete this unit\? All the unit data will be deleted permanently/i
		);

		//Click the cancel button to remove the modal
		const cancelBtn = screen.getByText(/Cancel/i);
		await fireEvent.click(cancelBtn);
		expect(modalText).not.toBeInTheDocument();
	});
});
