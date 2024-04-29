/* eslint-disable no-undef */
import {
	validateCourseId,
	validateCourseSemester,
	validateCourseName,
	validateUnitTitle,
	validateEmailAddresses,
	validateInviteRole,
	validateUnitDate
} from '../../src/lib/validation';

describe('Course ID Validation', () => {
	it('should complain if the course ID is empty', () => {
		expect(validateCourseId('')).toEqual([
			'Must not be empty',
			'Must be over 4 characters',
			'Must contain at least one letter and one number'
		]);
	});

	it('should require one letter and one number', () => {
		expect(validateCourseId('aaaa')).toBe('Must contain at least one letter and one number');
	});

	it('should require course ID to be over 4 characters', () => {
		expect(validateCourseId('a1b')).toBe('Must be over 4 characters');
	});

	it('should pass with valid course ID', () => {
		expect(validateCourseId('c1de')).toBeUndefined();
	});
});

describe('Course Semester Validation', () => {
	it('should require a choice', () => {
		expect(validateCourseSemester('')).toEqual(['Must choose one option!']);
	});

	it('should pass if any option is chosen', () => {
		expect(validateCourseSemester('Spring 2022')).toBeUndefined();
	});
});

describe('Course Name Validation', () => {
	it('should complain if the name is empty', () => {
		expect(validateCourseName('')).toEqual(['Must not be empty', 'Must be over 4 characters']);
	});

	it('should require name to be over 4 characters', () => {
		expect(validateCourseName('abc')).toBe('Must be over 4 characters');
	});

	it('should pass with a valid name', () => {
		expect(validateCourseName('Algebra')).toBeUndefined();
	});
});

describe('Unit Title Validation', () => {
	it('should complain if the title is empty', () => {
		expect(validateUnitTitle('')).toEqual(['Must not be empty', 'Must be over 4 characters']);
	});

	it('should require title to be over 4 characters', () => {
		expect(validateUnitTitle('uni')).toBe('Must be over 4 characters');
	});

	it('should pass with a valid title', () => {
		expect(validateUnitTitle('Introduction')).toBeUndefined();
	});
});

describe('Email Address Validation', () => {
	it('should complain if email addresses are empty', () => {
		expect(validateEmailAddresses('')).toBe('Cannot be empty');
	});

	it('should not allow emails with @stud.ntnu.no', () => {
		expect(validateEmailAddresses('test@stud.ntnu.no')).toBe('Cannot include @stud');
	});

	it('should require emails to include @ntnu.no', () => {
		expect(validateEmailAddresses('test@gmail.com')).toBe('Must include @ntnu.no');
	});

	it('should pass with valid email address', () => {
		expect(validateEmailAddresses('test@ntnu.no')).toBeUndefined();
	});
});

describe('Invite Role Validation', () => {
	it('should require a choice of role', () => {
		expect(validateInviteRole('')).toEqual(['Must choose one option!']);
	});

	it('should pass if any role is chosen', () => {
		expect(validateInviteRole('Instructor')).toBeUndefined();
	});
});

describe('Unit Date Validation', () => {
	it('should complain if the date is empty', () => {
		expect(validateUnitDate('')).toEqual(['Must not be empty', 'Must be over 4 characters']);
	});

	it('should require date to be over 4 characters', () => {
		expect(validateUnitDate('May')).toBe('Must be over 4 characters');
	});

	it('should pass with a valid date', () => {
		expect(validateUnitDate('May 10, 2024')).toBeUndefined();
	});
});
