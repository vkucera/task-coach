//
//  TaskDetailsDates.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 16/05/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "TaskCoachAppDelegate.h"

#import "TaskDetailsDates.h"
#import "CellFactory.h"
#import "DatePickerViewController.h"
#import "DateUtils.h"

#import "CDTask.h"
#import "CDTask+Addons.h"
#import "CDDomainObject+Addons.h"

#import "i18n.h"

@implementation TaskDetailsDates

- initWithTask:(CDTask *)theTask parent:(TaskDetailsController *)parent
{
	if (self = [super initWithNibName:@"TaskDetailsDates" bundle:[NSBundle mainBundle]])
	{
		task = [theTask retain];
		parentCtrl = parent;
		
		cells = [[NSMutableArray alloc] initWithCapacity:3];

		startDateCell = [[CellFactory cellFactory] createDateCell];
		[startDateCell setDelegate:self];
		startDateCell.label.text = _("Start");
		[startDateCell setDate:theTask.startDate];
		[cells addObject:startDateCell];
		
		dueDateCell = [[CellFactory cellFactory] createDateCell];
		[dueDateCell setDelegate:self];
		dueDateCell.label.text = _("Due");
		[dueDateCell setDate:theTask.dueDate];
		[cells addObject:dueDateCell];
		
		completionDateCell = [[CellFactory cellFactory] createDateCell];
		[completionDateCell setDelegate:self];
		completionDateCell.label.text = _("Completion");
		[completionDateCell setDate:theTask.completionDate];
		[cells addObject:completionDateCell];

		reminderDateCell = [[CellFactory cellFactory] createDateCell];
		[reminderDateCell setDelegate:self];
		reminderDateCell.label.text = _("Reminder");
		[reminderDateCell setDate:theTask.reminderDate];
		[cells addObject:reminderDateCell];

		datePicker = [[DatePickerViewController alloc] initWithDate:nil target:self action:@selector(onPickStartDate:)];
		datePicker.view.hidden = YES;
		[parentCtrl.view addSubview:datePicker.view];
	}

	return self;
}

- (void)dealloc
{
	[datePicker.view removeFromSuperview];
	[datePicker release];

	[cells release];
	[task release];

	[super dealloc];
}

#pragma mark Date stuff

- (void)presentDatePicker
{
	[UIView beginAnimations:@"DatePickerAnimation" context:nil];
	[UIView setAnimationDuration:1.0];
	[UIView setAnimationTransition:UIViewAnimationTransitionCurlDown forView:parentCtrl.view cache:YES];
	datePicker.view.hidden = NO;
	[UIView commitAnimations];
}

- (void)dismissDatePicker
{
	[UIView beginAnimations:@"DatePickerAnimation" context:nil];
	[UIView setAnimationDuration:1.0];
	[UIView setAnimationTransition:UIViewAnimationTransitionCurlUp forView:parentCtrl.view cache:YES];
	datePicker.view.hidden = YES;
	[UIView commitAnimations];
}

- (void)onSwitchValueChanged:(SwitchCell *)cell
{
	if (cell == startDateCell)
	{
		if (cell.switch_.on)
		{
			[datePicker setDate:task.startDate target:self action:@selector(onPickStartDate:)];
			[self presentDatePicker];
		}
		else
		{
			[startDateCell setDate:nil];

			task.startDate = nil;
			[task computeDateStatus];
			[task markDirty];

			NSError *error;
			if (![getManagedObjectContext() save:&error])
			{
				UIAlertView *alert = [[UIAlertView alloc] initWithTitle:_("Error") message:_("Could not save task.") delegate:self cancelButtonTitle:_("OK") otherButtonTitles:nil];
				[alert show];
				[alert release];
			}
		}
	}
	else if (cell == dueDateCell)
	{
		if (cell.switch_.on)
		{
			NSDate *date = nil;
			
			if (task.dueDate)
				date = task.dueDate;
			else if (task.startDate)
				date = task.startDate;
			
			[datePicker setDate:date target:self action:@selector(onPickDueDate:)];
			[self presentDatePicker];
		}
		else
		{
			[dueDateCell setDate:nil];

			task.dueDate = nil;
			[task computeDateStatus];
			[task markDirty];

			NSError *error;
			if (![getManagedObjectContext() save:&error])
			{
				UIAlertView *alert = [[UIAlertView alloc] initWithTitle:_("Error") message:_("Could not save task.") delegate:self cancelButtonTitle:_("OK") otherButtonTitles:nil];
				[alert show];
				[alert release];
			}
		}
	}
	else if (cell == completionDateCell)
	{
		if (cell.switch_.on)
		{
			[datePicker setDate:task.completionDate target:self action:@selector(onPickCompletionDate:)];
			[self presentDatePicker];
		}
		else
		{
			[completionDateCell setDate:nil];

			task.completionDate = nil;
			[task computeDateStatus];
			[task markDirty];

			NSError *error;
			if (![getManagedObjectContext() save:&error])
			{
				UIAlertView *alert = [[UIAlertView alloc] initWithTitle:_("Error") message:_("Could not save task.") delegate:self cancelButtonTitle:_("OK") otherButtonTitles:nil];
				[alert show];
				[alert release];
			}
		}
	}
	else if (cell == reminderDateCell)
	{
		if (cell.switch_.on)
		{
			[datePicker setDate:task.reminderDate target:self action:@selector(onPickReminder:)];
			[self presentDatePicker];
		}
		else
		{
			[reminderDateCell setDate:nil];

			task.reminderDate = nil;
			[task markDirty];

			NSError *error;
			if (![getManagedObjectContext() save:&error])
			{
				UIAlertView *alert = [[UIAlertView alloc] initWithTitle:_("Error") message:_("Could not save task.") delegate:self cancelButtonTitle:_("OK") otherButtonTitles:nil];
				[alert show];
				[alert release];
			}
		}
	}
}

- (void)onPickStartDate:(NSDate *)date
{
	[self dismissDatePicker];

	if (date)
	{
		task.startDate = date;
		
		if (task.dueDate)
		{
			NSDate *dueDate = task.dueDate;
			if ([dueDate compare:date] == NSOrderedAscending)
			{
				NSDate *date = task.startDate;
				date = [date addTimeInterval:3600];
				task.dueDate = date;
			}
		}
	}
	else if (!task.startDate)
	{
		[startDateCell.switch_ setOn:NO animated:YES];
	}
	
	[task computeDateStatus];
	[task markDirty];

	NSError *error;
	if (![getManagedObjectContext() save:&error])
	{
		UIAlertView *alert = [[UIAlertView alloc] initWithTitle:_("Error") message:_("Could not save task.") delegate:self cancelButtonTitle:_("OK") otherButtonTitles:nil];
		[alert show];
		[alert release];
	}
	
	[startDateCell setDate:task.startDate];
	[dueDateCell setDate:task.dueDate];
}

- (void)onPickDueDate:(NSDate *)date
{
	[self dismissDatePicker];

	if (date)
	{
		task.dueDate = date;
		
		if (task.startDate)
		{
			NSDate *startDate = task.startDate;
			if ([startDate compare:date] == NSOrderedDescending)
			{
				// Substract one hour ?
				task.startDate = task.dueDate;
			}
		}
	}
	else if (!task.dueDate)
	{
		[dueDateCell.switch_ setOn:NO animated:YES];
	}
	
	[task computeDateStatus];
	[task markDirty];

	NSError *error;
	if (![getManagedObjectContext() save:&error])
	{
		UIAlertView *alert = [[UIAlertView alloc] initWithTitle:_("Error") message:_("Could not save task.") delegate:self cancelButtonTitle:_("OK") otherButtonTitles:nil];
		[alert show];
		[alert release];
	}
	
	[startDateCell setDate:task.startDate];
	[dueDateCell setDate:task.dueDate];
}

- (void)onPickCompletionDate:(NSDate *)date
{
	[self dismissDatePicker];
	
	task.completionDate = date;
	[task computeDateStatus];
	[task markDirty];

	NSError *error;
	if (![getManagedObjectContext() save:&error])
	{
		UIAlertView *alert = [[UIAlertView alloc] initWithTitle:_("Error") message:_("Could not save task.") delegate:self cancelButtonTitle:_("OK") otherButtonTitles:nil];
		[alert show];
		[alert release];
	}

	[completionDateCell setDate:task.completionDate];
}

- (void)onPickReminder:(NSDate *)date
{
	[self dismissDatePicker];

	task.reminderDate = date;
	[task computeDateStatus];
	[task markDirty];

	NSError *error;
	if (![getManagedObjectContext() save:&error])
	{
		UIAlertView *alert = [[UIAlertView alloc] initWithTitle:_("Error") message:_("Could not save task.") delegate:self cancelButtonTitle:_("OK") otherButtonTitles:nil];
		[alert show];
		[alert release];
	}

	[reminderDateCell setDate:task.reminderDate];
}

#pragma mark Table view methods

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView
{
    return 1;
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

	if (cell == startDateCell)
	{
		[datePicker setDate:task.startDate target:self action:@selector(onPickStartDate:)];
	}
	else if (cell == dueDateCell)
	{
		[datePicker setDate:task.dueDate target:self action:@selector(onPickDueDate:)];
	}
	else if (cell == completionDateCell)
	{
		[datePicker setDate:task.completionDate target:self action:@selector(onPickCompletionDate:)];
	}
	else if (cell == reminderDateCell)
	{
		[datePicker setDate:task.reminderDate target:self action:@selector(onPickReminder:)];
	}

	[self presentDatePicker];
}

@end

