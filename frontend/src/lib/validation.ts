/**
 * Validate the course ID input in creation of course
 * @param courseId The course ID to validate
 * @returns An array of error messages if the input is invalid, less than 4 characters,
 * does not contain at least one letter and one number
 */
export function validateCourseId(courseId: string) {
	if (!courseId) {
		return [
			'Must not be empty',
			'Must be over 4 characters',
			'Must contain at least one letter and one number'
		];
	} else if (!/^(?=.*[a-zA-Z])(?=.*[0-9])/.test(courseId)) {
		return 'Must contain at least one letter and one number';
	} else if (courseId.length < 4) {
		return 'Must be over 4 characters';
	}
}

/**
 * Validate the course semester input in creation of course
 * @param semester The course semester to validate
 * @returns An array of error messages if the input is invalid
 */
export function validateCourseSemester(semester: string) {
	if (!semester) {
		return ['Must choose one option!'];
	}
}

/**
 * Validate the course name input in creation of course
 * @param name The course name to validate
 * @returns An array of error messages if the input is invalid, less than 4 characters
 */
export function validateCourseName(name: string) {
	if (!name) {
		return ['Must not be empty', 'Must be over 4 characters'];
	} else if (name.length < 4) {
		return 'Must be over 4 characters';
	}
}

/**
 * Validate the unit title input in unit creation
 * @param name The unit title to validate
 * @returns An array of error messages if the input is invalid, less than 4 characters
 */
export function validateUnitTitle(name: string) {
	if (!name) {
		return ['Must not be empty', 'Must be over 4 characters'];
	} else if (name.length < 4) {
		return 'Must be over 4 characters';
	}
}

/**
 * Validate the email address input
 * @param emailAdresses The email address to validate
 * @returns An array of error messages if the email address is invalid, empty, contains @stud.ntnu.no or does not contain @ntnu.no
 */
export function validateEmailAddresses(emailAdresses: string) {
	const emailList = emailAdresses.split(' ');
	if (!emailAdresses) {
		return 'Cannot be empty';
	}

	for (let i = 0; i < emailList.length; i++) {
		if (emailList[i].includes('@stud.ntnu.no')) {
			return 'Cannot include @stud';
		}
		if (!emailList[i].includes('@ntnu.no')) {
			return 'Must include @ntnu.no';
		}
	}
}

/**
 * Validate the invite role input
 * @param inviteRole The invite role to validate
 * @returns An error message if the input is invalid
 */
export function validateInviteRole(inviteRole: string) {
	if (!inviteRole) {
		return ['Must choose one option!'];
	}
}

/**
 * Validate the unit date input in unit creation
 * @param name The unit date to validate
 * @returns An array of error messages if the input is invalid, less than 4 characters
 */
export function validateUnitDate(name: string) {
	if (!name) {
		return ['Must not be empty', 'Must be over 4 characters'];
	} else if (name.length < 4) {
		return 'Must be over 4 characters';
	}
}

//validate unit title input in creation of unit
/*
export function validateUnitSeqNumber(name: string) {
	if (!name) {
		return ['Must not be empty', 'Must be over 4 characters'];
	} else if (name.length < 4) {
		return 'Must be over 4 characters';
	}
}
*/
