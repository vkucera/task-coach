//
//  TaskDetailsController-iPad.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/06/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "TaskCoachAppDelegate.h"
#import "TaskDetailsControlleriPad.h"
#import "TaskCategoryPickerController.h"
#import "TaskDetailsEffortsBase.h"
#import "TaskDetailsRecurrenceControlleriPad.h"
#import "DateUtils.h"
#import "String+Utils.h"
#import "i18n.h"
#import "Configuration.h"

#import "SimpleDatePicker.h"

#import "CDTask.h"
#import "CDTask+Addons.h"
#import "CDDomainObject+Addons.h"
#import "CDFile.h"
#import "CDCategory.h"

@interface TaskDetailsControlleriPad ()

- (void)onSaveDescription:(UIBarButtonItem *)button;
- (void)refreshButtons;
- (void)saveTask;

@end

@implementation TaskDetailsControlleriPad

@synthesize subject;
@synthesize description;
@synthesize startDateButton;
@synthesize dueDateButton;
@synthesize completionDateButton;
@synthesize reminderDateButton;
@synthesize priorityLabel;
@synthesize recurrenceButton;
@synthesize effortButton;
@synthesize categoryButton;
@synthesize prioritySlider;

@synthesize taskCatCtrl;
@synthesize taskEffortCtrl;

- initWithTask:(CDTask *)theTask
{
	if ((self = [super initWithNibName:@"TaskDetailsControlleriPad" bundle:[NSBundle mainBundle]]))
	{
		task = [theTask retain];

		datePicker = [[SimpleDatePicker alloc] initWithTarget:self action:@selector(onPickedDate)];
	}

	return self;
}

- (void)viewDidLoad
{
	[super viewDidLoad];

	self.navigationItem.title = task.name;

	self.subject.text = task.name;
	self.description.text = task.longDescription;

	[self refreshButtons];

	if (![task.name length])
		[subject becomeFirstResponder];

	[taskCatCtrl setTask:task];
	[taskEffortCtrl setTask:task];
	[taskEffortCtrl updateButton:effortButton];

	self.prioritySlider.value = (float)[task.priority intValue];
}

- (void)viewDidUnload
{
	self.subject = nil;
	self.description = nil;
	self.startDateButton = nil;
	self.dueDateButton = nil;
	self.completionDateButton = nil;
	self.reminderDateButton = nil;
	self.priorityLabel = nil;
	self.recurrenceButton = nil;
	self.effortButton = nil;
	self.taskCatCtrl = nil;
	self.taskEffortCtrl = nil;
	self.categoryButton = nil;
	self.prioritySlider = nil;
}

- (void)dealloc
{
	[self viewDidUnload];

	[datePicker release];

	[super dealloc];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
	if (popoverCtrl)
	{
		[popoverCtrl dismissPopoverAnimated:YES];
	}

    return YES;
}

- (void)didRotateFromInterfaceOrientation:(UIInterfaceOrientation)fromInterfaceOrientation
{
	if (popoverCtrl)
	{
		UIButton *button;

		if (popoverCtrl.contentViewController == taskCatCtrl)
			button = categoryButton;
		else
		{
			if (dateName)
			{
				if ([dateName isEqualToString:@"startDate"])
					button = startDateButton;
				else if ([dateName isEqualToString:@"dueDate"])
					button = dueDateButton;
				else if ([dateName isEqualToString:@"completionDate"])
					button = completionDateButton;
				else
					button = reminderDateButton;
			}
			else
				button = recurrenceButton;
		}
			
		[popoverCtrl presentPopoverFromRect:button.frame inView:self.view permittedArrowDirections:UIPopoverArrowDirectionAny animated:YES];
	}
}

- (void)refreshButtons
{
	if (task.startDate)
		[self.startDateButton setTitle:[NSString stringWithFormat:_("Started %@"), [[UserTimeUtils instance] stringFromDate:task.startDate]] forState:UIControlStateNormal];
	else
		[self.startDateButton setTitle:_("No start date") forState:UIControlStateNormal];
	
	if (task.dueDate)
		[self.dueDateButton setTitle:[NSString stringWithFormat:_("Due %@"), [[UserTimeUtils instance] stringFromDate:task.dueDate]] forState:UIControlStateNormal];
	else
		[self.dueDateButton setTitle:_("No due date") forState:UIControlStateNormal];
	
	if (task.completionDate)
		[self.completionDateButton setTitle:[NSString stringWithFormat:_("Completed %@"), [[UserTimeUtils instance] stringFromDate:task.completionDate]] forState:UIControlStateNormal];
	else
		[self.completionDateButton setTitle:_("No completion date") forState:UIControlStateNormal];
	
	if (task.reminderDate)
		[self.reminderDateButton setTitle:[NSString stringWithFormat:_("Reminder %@"), [[UserTimeUtils instance] stringFromDate:task.reminderDate]] forState:UIControlStateNormal];
	else
		[self.reminderDateButton setTitle:_("No reminder") forState:UIControlStateNormal];

	priorityLabel.text = [NSString stringWithFormat:_("%@"), task.priority];

	if ([task.categories count])
	{
		NSMutableArray *cats = [[NSMutableArray alloc] init];
		for (CDCategory *cat in task.categories)
			[cats addObject:cat.name];
		[categoryButton setTitle:[@", " stringByJoiningStrings:cats] forState:UIControlStateNormal];
	}
	else
	{
		[categoryButton setTitle:_("No category.") forState:UIControlStateNormal];
	}

	priorityLabel.textColor = [UIColor colorWithRed:1.0 * [task.priority intValue] / 15 green:1.0 - 1.0 * [task.priority intValue] / 15 blue:0 alpha:1];
}

- (void)saveTask
{
	[task markDirty];
	NSError *error;
	if (![getManagedObjectContext() save:&error])
	{
		UIAlertView *alert = [[UIAlertView alloc] initWithTitle:_("Error") message:_("Could not save task.") delegate:self cancelButtonTitle:_("OK") otherButtonTitles:nil];
		[alert show];
		[alert release];
	}
}

#pragma mark Actions

- (IBAction)onClickDate:(UIButton *)button
{
	[description resignFirstResponder];

	NSDateComponents *comp = [[NSCalendar currentCalendar] components:NSYearCalendarUnit|NSMonthCalendarUnit|NSDayCalendarUnit fromDate:[NSDate date]];
	[comp setHour:0];
	[comp setMinute:0];
	[comp setSecond:0];

	if (button == startDateButton)
	{
		dateName = @"startDate";

		if ([Configuration configuration].cdCurrentFile)
			[comp setHour:[[Configuration configuration].cdCurrentFile.startHour intValue]];
		else
			[comp setHour:8];
	}
	else if (button == dueDateButton)
	{
		dateName = @"dueDate";
		if ([Configuration configuration].cdCurrentFile)
			[comp setHour:[[Configuration configuration].cdCurrentFile.endHour intValue]];
		else
			[comp setHour:18];
	}
	else if (button == completionDateButton)
	{
		dateName = @"completionDate";
		comp = [[NSCalendar currentCalendar] components:NSYearCalendarUnit|NSMonthCalendarUnit|NSDayCalendarUnit|NSHourCalendarUnit|NSMinuteCalendarUnit fromDate:[NSDate date]];
	}
	else if (button == reminderDateButton)
	{
		dateName = @"reminderDate";
		if (task.dueDate)
			comp = [[NSCalendar currentCalendar] components:NSYearCalendarUnit|NSMonthCalendarUnit|NSDayCalendarUnit|NSHourCalendarUnit|NSMinuteCalendarUnit fromDate:task.dueDate];
		else if (task.startDate)
			comp = [[NSCalendar currentCalendar] components:NSYearCalendarUnit|NSMonthCalendarUnit|NSDayCalendarUnit|NSHourCalendarUnit|NSMinuteCalendarUnit fromDate:task.startDate];
		else
		{
			if ([Configuration configuration].cdCurrentFile)
				[comp setHour:[[Configuration configuration].cdCurrentFile.endHour intValue]];
			else
				[comp setHour:18];
		}
	}
	else
	{
		assert(0);
	}

	NSDate *theDate = [task valueForKey:dateName];
	if (!theDate)
		theDate = [[NSCalendar currentCalendar] dateFromComponents:comp];
	datePicker.date = theDate;

	popoverCtrl = [[UIPopoverController alloc] initWithContentViewController:datePicker];
	[popoverCtrl setPopoverContentSize:CGSizeMake(320, 281) animated:NO];
	[popoverCtrl presentPopoverFromRect:button.frame inView:self.view permittedArrowDirections:UIPopoverArrowDirectionAny animated:YES];
	popoverCtrl.delegate = self;
}

- (void)onPickedDate
{
	[task setValue:datePicker.date forKey:dateName];
	dateName = nil;
	[task computeDateStatus];
	[self saveTask];

	[popoverCtrl dismissPopoverAnimated:YES]; // This doesn't call popoverControllerDidDismissPopover
	[popoverCtrl release];
	popoverCtrl = nil;

	[self refreshButtons];
}

- (IBAction)onPriorityChanged:(UISlider *)slider
{
	[description resignFirstResponder];
	
	task.priority = [NSNumber numberWithInt:(int)slider.value];
	[self saveTask];
	[self refreshButtons];
}

- (IBAction)onClickEffort:(UIButton *)button
{
	[description resignFirstResponder];
	
	[taskEffortCtrl onTrack:button];
}

- (IBAction)onClickRecurrence:(UIButton *)button
{
	[description resignFirstResponder];
	
	TaskDetailsRecurrenceControlleriPad *ctrl = [[TaskDetailsRecurrenceControlleriPad alloc] initWithTask:task];
	popoverCtrl = [[UIPopoverController alloc] initWithContentViewController:ctrl];
	popoverCtrl.delegate = self;
	[popoverCtrl setPopoverContentSize:CGSizeMake(284, 141)];
	[popoverCtrl presentPopoverFromRect:button.frame inView:self.view permittedArrowDirections:UIPopoverArrowDirectionAny animated:YES];
	[ctrl release];
}

- (IBAction)onPickCategories:(UIButton *)button
{
	[description resignFirstResponder];
	
	popoverCtrl = [[UIPopoverController alloc] initWithContentViewController:taskCatCtrl];
	popoverCtrl.delegate = self;
	[popoverCtrl setPopoverContentSize:CGSizeMake(300, 400)];
	[popoverCtrl presentPopoverFromRect:button.frame inView:self.view permittedArrowDirections:UIPopoverArrowDirectionAny animated:YES];
}

#pragma mark UIPopoverControllerDelegate

- (void)popoverControllerDidDismissPopover:(UIPopoverController *)popoverController
{
	if (popoverController.contentViewController != taskCatCtrl)
	{
		if (dateName)
		{
			[task setValue:nil forKey:dateName];
			dateName = nil;
			[task computeDateStatus];
			[self saveTask];
		}
	}
	
	[popoverCtrl release];
	popoverCtrl = nil;
	
	[self refreshButtons];
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
		task.name = _("New task");
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
	[self onSaveDescription:nil];
}

- (void)onSaveDescription:(UIBarButtonItem *)button
{
	[description resignFirstResponder];
	
	task.longDescription = description.text;
	[self saveTask];
}

@end
