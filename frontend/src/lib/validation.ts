//Validate the course name input in creation of course
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

//Validate the course ID input in creation of course
export function validateCourseSemester(semester: string) {
	if (!semester) {
		return ['Must choose one option!'];
	}
}

//Validate the course semester input in creation of course
export function validateCourseName(name: string) {
	if (!name) {
		return ['Must not be empty', 'Must be over 4 characters'];
	} else if (name.length < 4) {
		return 'Must be over 4 characters';
	}
}

//validate unit title input in creation of unit
export function validateUnitTitle(name: string) {
	if (!name) {
		return ['Must not be empty', 'Must be over 4 characters'];
	} else if (name.length < 4) {
		return 'Must be over 4 characters';
	}
}

//validate invitation emails
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

export function validateInviteRole(inviteRole: string) {
	if (!inviteRole) {
		return ['Must choose one option!'];
	}
}

//validate unit title input in creation of unit
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
