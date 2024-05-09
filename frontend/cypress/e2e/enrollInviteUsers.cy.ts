import loginUser from './loginUser';

const userName = Cypress.env('FEIDE_USERNAME');

describe('Check functionality for inviting and enrolling users', () => {
	beforeEach(() => {
		loginUser();
	});

	it('Create course, then invite myself to course and check that notification arrive', () => {
		// Create new course
		cy.get('#createCourseButton').click();
		cy.get('#courseNameInput').type('Test Course');
		cy.get('#courseIdInput').type('TDT1234');
		cy.get('#selectSemester').select('Spring 2025');
		cy.get('#createCourseSubmit').click();
		cy.get('#TDT1234').click();

		// Invite myself to the course
		cy.get('#inviteUsersButton').click();
		cy.get('#inviteUsersModal').should('be.visible');
		cy.get('#enrollLecturer').type(userName);
		cy.get('#enrollLecturerButton').click();
		cy.contains('Invitation sent successfully').should('be.visible');
		cy.reload();

		// Check that notification has arrived
		cy.wait(1000);
		cy.get('#invitationCountNotification').should('be.visible');
		cy.get('#mailIconDiv').click();
		cy.get('#invitationDropdown').should('be.visible');
		cy.get('#invitationDropdown').click();
		cy.get('#answerInvitationModal').should('be.visible');

		// Cannot accept invitation as the user is already enrolled
		cy.get('#declineInvitationButton').click();

		// Delete course after test to clean up
		cy.get('#deleteCourseButton').click();
		cy.get('#deleteCourseModalButton').click();
		cy.contains('Course successfully deleted!').should('be.visible');
	});

	it('Unenroll from coure and then eroll to course again', () => {
		// Unenroll from TDT4100 course
		cy.get('#TDT4100').click();
		cy.get('#deleteCourseButton').click();
		cy.get('#deleteCourseModal').should('be.visible');
		cy.get('#deleteCourseModalButton').click();

		// Check that course has disappeared from overview
		cy.contains('Unenrolled from course successfully!').should('be.visible');
		cy.get('#TDT4100').should('not.exist');
		cy.contains('You are not enrolled to any course yet').should('be.visible');
		cy.wait(2000);

		// Enroll to course again by visiting enroll link
		cy.visit('http://127.0.0.1:5173/enroll/fall2023/TDT4100');
		cy.get('#TDT4100').should('be.visible');
	});
});
