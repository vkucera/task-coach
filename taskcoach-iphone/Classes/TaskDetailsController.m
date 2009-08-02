//
//  TaskDetailsController.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 19/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "TaskDetailsController.h"
#import "DatePickerViewController.h"
#import "TaskCategoryPickerController.h"

#import "Task.h"

#import "CellFactory.h"
#import "TextFieldCell.h"
#import "DescriptionCell.h"

#import "DateUtils.h"
#import "Database.h"
#import "Statement.h"

//======================================================================

@implementation TaskDetailsController

- initWithTask:(Task *)theTask category:(NSInteger)category
{
	if (self = [super initWithNibName:@"TaskDetails" bundle:[NSBundle mainBundle]])
	{
		task = [theTask retain];
		categoryId = category;

		cells = [[NSMutableArray alloc] initWithCapacity:5];

		SwitchCell *completeCell = [[CellFactory cellFactory] createSwitchCell];
		[completeCell setDelegate:self];
		completeCell.label.text = NSLocalizedString(@"Complete", @"Task details complete label");
		[completeCell.switch_ setOn:(task.completionDate != nil)];
		[cells addObject:completeCell];
		
		TextFieldCell *nameCell = [[CellFactory cellFactory] createTextFieldCell];
		nameCell.textField.delegate = self;
		nameCell.textField.text = task.name;
		[cells addObject:nameCell];
		
		descriptionCell = [[CellFactory cellFactory] createDescriptionCell];
		descriptionCell.textView.delegate = self;
		descriptionCell.textView.text = task.description;
		[cells addObject:descriptionCell];
		
		categoriesCell = [[UITableViewCell alloc] initWithFrame:CGRectZero];
		categoriesCell.text = NSLocalizedString(@"Categories", @"Categories cell text in task details");
		categoriesCell.accessoryType = UITableViewCellAccessoryDisclosureIndicator;
		[cells addObject:categoriesCell];
		[categoriesCell release];

		startDateCell = [[CellFactory cellFactory] createDateCell];
		[startDateCell setDelegate:self];
		startDateCell.label.text = NSLocalizedString(@"Start date", @"Task details start date label");
		[startDateCell setDate:task.startDate];
		[cells addObject:startDateCell];
		
		dueDateCell = [[CellFactory cellFactory] createDateCell];
		[dueDateCell setDelegate:self];
		dueDateCell.label.text = NSLocalizedString(@"Due date", @"Task details due date label");
		[dueDateCell setDate:task.dueDate];
		[cells addObject:dueDateCell];
	}

	return self;
}

- (void)dealloc
{
	[task release];
	[cells release];

	[super dealloc];
}

- (void)saveTask
{
	BOOL isNew = (task.objectId == -1);
	[task save];
	
	if (isNew && (categoryId != -1))
	{
		Statement *req = [[Database connection] statementWithSQL:@"INSERT INTO TaskHasCategory (idTask, idCategory) VALUES (?, ?)"];
		[req bindInteger:task.objectId atIndex:1];
		[req bindInteger:categoryId atIndex:2];
		[req exec];
	}
}

- (void)viewDidLoad
{
	if (task.objectId == -1)
	{
		// New task.
		TextFieldCell *cell = [cells objectAtIndex:1];
		[cell.textField becomeFirstResponder];
		self.navigationItem.title = NSLocalizedString(@"New task", @"New task editing title");
	}
	else
	{
		self.navigationItem.title = task.name;
	}
}

- (void)onSwitchValueChanged:(SwitchCell *)cell
{
	if (cell == startDateCell)
	{
		if (cell.switch_.on)
		{
			DatePickerViewController *ctrl = [[DatePickerViewController alloc] initWithDate:task.startDate target:self action:@selector(onPickStartDate:)];
			[self.navigationController presentModalViewController:ctrl animated:YES];
			[ctrl release];
		}
		else
		{
			task.startDate = nil;
			[self saveTask];
			[startDateCell setDate:nil];
		}
	}
	else if (cell == dueDateCell)
	{
		if (cell.switch_.on)
		{
			DatePickerViewController *ctrl = [[DatePickerViewController alloc] initWithDate:task.dueDate target:self action:@selector(onPickDueDate:)];
			[self.navigationController presentModalViewController:ctrl animated:YES];
			[ctrl release];
		}
		else
		{
			task.dueDate = nil;
			[self saveTask];
			[dueDateCell setDate:nil];
		}
	}
	else
	{
		[task setCompleted:cell.switch_.on];
		[self saveTask];
	}
}

- (void)onPickStartDate:(NSDate *)date
{
	[self.navigationController dismissModalViewControllerAnimated:YES];
	
	if (date)
	{
		task.startDate = [[DateUtils instance] stringFromDate:date];
	}
	else if (!task.startDate)
	{
		[startDateCell.switch_ setOn:NO animated:YES];
	}
	
	[self saveTask];
	[startDateCell setDate:task.startDate];
}

- (void)onPickDueDate:(NSDate *)date
{
	[self.navigationController dismissModalViewControllerAnimated:YES];
	
	if (date)
	{
		task.dueDate = [[DateUtils instance] stringFromDate:date];
	}
	else if (!task.dueDate)
	{
		[dueDateCell.switch_ setOn:NO animated:YES];
	}
	
	[self saveTask];
	[dueDateCell setDate:task.dueDate];
}

#pragma mark Table view methods

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView
{
    return 1;
}

- (NSString *)tableView:(UITableView *)tableView titleForHeaderInSection:(NSInteger)section
{
	return @"";
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section
{
	return [cells count];
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath
{
	return [cells objectAtIndex:indexPath.row];
}

- (void)tableView:(UITableView *)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath
{
	UITableViewCell *cell = [cells objectAtIndex:indexPath.row];
	UIViewController *ctrl = nil;

	if (cell == categoriesCell)
	{
		TaskCategoryPickerController *categoryPicker = [[TaskCategoryPickerController alloc] initWithTask:task];
		[self.navigationController pushViewController:categoryPicker animated:YES];
		[categoryPicker release];
	}
	else if (cell == startDateCell)
	{
		ctrl = [[DatePickerViewController alloc] initWithDate:task.startDate target:self action:@selector(onPickStartDate:)];
	}
	else if (cell == dueDateCell)
	{
		ctrl = [[DatePickerViewController alloc] initWithDate:task.dueDate target:self action:@selector(onPickDueDate:)];
	}

	if (ctrl)
	{
		[self.navigationController presentModalViewController:ctrl animated:YES];
		[ctrl release];
	}
}

- (CGFloat)tableView:(UITableView *)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath
{
	UITableViewCell *cell = [cells objectAtIndex:indexPath.row];
	
	if (cell == descriptionCell)
		return 180;
	return 44;
}

#pragma mark UITextFieldDelegate protocol

- (BOOL)textFieldShouldReturn:(UITextField *)textField
{
	[textField resignFirstResponder];
	return NO;
}

- (void)textFieldDidEndEditing:(UITextField *)textField
{
	if ([textField.text length])
	{
		task.name = textField.text;
	}
	else
	{
		task.name = NSLocalizedString(@"New task", @"New task subject");
		textField.text = task.name;
	}

	[self saveTask];
	self.navigationItem.title = task.name;
}

#pragma mark UITextViewDelegate protocol

- (BOOL)textViewShouldBeginEditing:(UITextView *)textView
{
	UIBarButtonItem *button = [[UIBarButtonItem alloc] initWithBarButtonSystemItem:UIBarButtonSystemItemSave target:self action:@selector(onSaveDescription:)];
	self.navigationItem.rightBarButtonItem = button;
	[button release];
	
	return YES;
}

- (void)textViewDidEndEditing:(UITextView *)textView
{
	self.navigationItem.rightBarButtonItem = nil;
	task.description = descriptionCell.textView.text;
	[self saveTask];
}

- (void)onSaveDescription:(UIBarButtonItem *)button
{
	[descriptionCell.textView resignFirstResponder];
}

@end

