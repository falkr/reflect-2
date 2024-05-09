import loginUser from './loginUser';

describe('Create new unit, then edit the unit and finally delete it', () => {
	beforeEach(() => {
		loginUser();
	});

	it('Create course, then create and edit unit, and finally delete the unit', () => {
		// Create new course
		cy.get('#createCourseButton').click();
		cy.get('#createCourseModal').should('be.visible');
		cy.get('#courseNameInput').type('Test Course');
		cy.get('#courseIdInput').type('TDT1234');
		cy.get('#selectSemester').select('Spring 2025');
		cy.get('#createCourseSubmit').click();

		// Check if the course is created
		cy.contains('Course successfully created!').should('be.visible');
		cy.get('#TDT1234').should('be.visible');
		cy.get('#lecturerBadge').should('be.visible');
		cy.get('#courseSemesterText').should('be.visible');
		cy.contains('TDT1234 - Test Course').should('be.visible');
		cy.contains('Spring 2025').should('be.visible');
		cy.get('#TDT1234').click();
		cy.wait(1000);

		// Create new unit
		cy.get('#createUnitButton').click();
		cy.url().should('include', '/courseview/spring2025/TDT1234/create');
		cy.get('#unitNameCreate').type('Test Unit');
		cy.get('#unitDateCreate').type('2025-12-12');
		cy.get('#createUnitSubmitButton').click();

		// Check that unit is created
		cy.contains('Unit created successfully').should('be.visible');
		cy.contains('Test Unit').should('be.visible');
		cy.contains('Unit 1 - 12.12.2025').should('be.visible');
		cy.contains('Not available').should('be.visible');
		cy.get('#editUnitButton').should('be.visible');

		// Edit unit
		cy.get('#editUnitButton').click();
		cy.get('#editUnitName').clear().type('Edited Unit');
		cy.get('#editUnitDate').clear().type('2025-12-12');
		cy.get('#editUnitSubmitButton').click();
		cy.wait(500);

		// Check that unit is edited
		cy.contains('Unit updated successfully').should('be.visible');
		cy.contains('Edited Unit').should('be.visible');
		cy.contains('Unit 1 - 12.12.2025').should('be.visible');
		cy.get('#editUnitButton').should('be.visible');

		// Delete the unit
		cy.get('#editUnitButton').click();
		cy.get('#deleteUnitButton').click();
		cy.get('#deleteUnitModal').should('be.visible');
		cy.contains(
			'Are you sure you want to delete this unit? All the unit data will be deleted permanently.'
		).should('be.visible');
		cy.get('#deleteUnitConfirmButton').click();
		cy.contains('Unit deleted successfully').should('be.visible');
		cy.wait(500);

		// Clean up by deleting the course
		cy.get('#deleteCourseButton').click();
		cy.get('#deleteCourseModal').should('be.visible');
		cy.get('#deleteCourseModalButton').click();
		cy.contains('Course successfully deleted!').should('be.visible');
	});
});
