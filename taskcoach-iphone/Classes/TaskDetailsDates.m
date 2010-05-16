//
//  TaskDetailsDates.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 16/05/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "TaskDetailsDates.h"
#import "CellFactory.h"
#import "Task.h"
#import "DatePickerViewController.h"
#import "DateUtils.h"
#import "i18n.h"

@implementation TaskDetailsDates

- initWithTask:(Task *)theTask parent:(TaskDetailsController *)parent
{
	if (self = [super initWithNibName:@"TaskDetailsDates" bundle:[NSBundle mainBundle]])
	{
		task = [theTask retain];
		parentCtrl = parent;
		
		cells = [[NSMutableArray alloc] initWithCapacity:3];

		startDateCell = [[CellFactory cellFactory] createDateCell];
		[startDateCell setDelegate:self];
		startDateCell.label.text = _("Start");
		[startDateCell setDate:task.startDate];
		[cells addObject:startDateCell];
		
		dueDateCell = [[CellFactory cellFactory] createDateCell];
		[dueDateCell setDelegate:self];
		dueDateCell.label.text = _("Due");
		[dueDateCell setDate:task.dueDate];
		[cells addObject:dueDateCell];
		
		completionDateCell = [[CellFactory cellFactory] createDateCell];
		[completionDateCell setDelegate:self];
		completionDateCell.label.text = _("Completion");
		[completionDateCell setDate:task.completionDate];
		[cells addObject:completionDateCell];

		datePicker = [[DatePickerViewController alloc] initWithDate:nil target:self action:@selector(onPickStartDate:)];
		datePicker.view.hidden = YES;
		[parentCtrl.view addSubview:datePicker.view];
	}

	return self;
}

- (void)viewDidLoad
{
	[super viewDidLoad];
}

- (void)viewDidUnload
{
}

- (void)dealloc
{
	[self viewDidUnload];

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
			task.startDate = nil;
			[task save];
			[startDateCell setDate:nil];
		}
	}
	else if (cell == dueDateCell)
	{
		if (cell.switch_.on)
		{
			NSString *date = nil;
			
			if (task.dueDate)
				date = task.dueDate;
			else if (task.startDate)
				date = task.startDate;
			
			[datePicker setDate:date target:self action:@selector(onPickDueDate:)];
			[self presentDatePicker];
		}
		else
		{
			task.dueDate = nil;
			[task save];
			[dueDateCell setDate:nil];
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
			task.completionDate = nil;
			[task save];
			[completionDateCell setDate:nil];
		}
	}
}

- (void)onPickStartDate:(NSDate *)date
{
	[self dismissDatePicker];
	
	if (date)
	{
		task.startDate = [[TimeUtils instance] stringFromDate:date];
		
		if (task.dueDate)
		{
			NSDate *dueDate = [[TimeUtils instance] dateFromString:task.dueDate];
			if ([dueDate compare:date] == NSOrderedAscending)
			{
				NSDate *date = [[TimeUtils instance] dateFromString:task.startDate];
				date = [date addTimeInterval:3600];
				task.dueDate = [[TimeUtils instance] stringFromDate:date];
			}
		}
	}
	else if (!task.startDate)
	{
		[startDateCell.switch_ setOn:NO animated:YES];
	}
	
	[task save];
	
	[startDateCell setDate:task.startDate];
	[dueDateCell setDate:task.dueDate];
}

- (void)onPickDueDate:(NSDate *)date
{
	[self dismissDatePicker];
	
	if (date)
	{
		task.dueDate = [[TimeUtils instance] stringFromDate:date];
		
		if (task.startDate)
		{
			NSDate *startDate = [[TimeUtils instance] dateFromString:task.startDate];
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
	
	[task save];
	
	[startDateCell setDate:task.startDate];
	[dueDateCell setDate:task.dueDate];
}

- (void)onPickCompletionDate:(NSDate *)date
{
	[self dismissDatePicker];
	
	if (date)
		task.completionDate = [[TimeUtils instance] stringFromDate:date];
	else
		task.completionDate = nil;
	
	[task save];
	[completionDateCell setDate:task.completionDate];
}

#pragma mark Table view methods

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView
{
    return 1;
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section
{
    return 3;
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

	[self presentDatePicker];
}

@end

