import loginUser from './loginUser';

describe('Check overview page and create/delete course', () => {
	beforeEach(() => {
		loginUser();
	});

	it('Try to write invalid input when creating course', () => {
		// Create new course
		cy.get('#createCourseButton').click();
		cy.get('#createCourseModal').should('be.visible');

		// No input
		cy.get('#createCourseSubmit').click();
		cy.contains('Must not be empty').should('be.visible');

		// Unvalid input
		cy.get('#courseNameInput').type('Test Course');
		cy.get('#courseIdInput').type('TDT');
		cy.get('#createCourseSubmit').click();
		cy.contains('Must contain at least one letter and one number').should('be.visible');

		// No semester selected
		cy.get('#courseIdInput').clear().type('TDT1234');
		cy.get('#createCourseSubmit').click();
		cy.contains('Must choose one option!').should('be.visible');
		cy.reload();
	});

	it('Display correct elements and create course', () => {
		// Check if the navbar breadcrumb, course and create button is visible
		cy.get('#navbar').should('be.visible');
		cy.contains('Courses').should('be.visible');
		cy.get('#TDT4100').should('be.visible');
		cy.get('#studentBadge').should('be.visible');
		cy.get('#createCourseButton').should('be.visible');

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
		cy.wait(1000);

		// Delete the course to clean up
		cy.get('#TDT1234').click();
		cy.get('#deleteCourseButton').click();
		cy.get('#deleteCourseModal').should('be.visible');
		cy.get('#deleteCourseModalButton').click();
		cy.contains('Course successfully deleted!').should('be.visible');
	});
});
