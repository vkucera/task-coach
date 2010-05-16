//
//  TaskDetailsEfforts.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 16/05/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "TaskDetailsEfforts.h"
#import "CellFactory.h"
#import "Database.h"
#import "Statement.h"
#import "DateUtils.h"
#import "Effort.h"
#import "String+Utils.h"
#import "Task.h"
#import "i18n.h"

@interface TaskDetailsEfforts ()

- (void)updateTrackButton;
- (void)updateEffortTotal;

@end;

@implementation TaskDetailsEfforts

- initWithTask:(Task *)theTask
{
	if (self = [super initWithNibName:@"TaskDetailsEfforts" bundle:[NSBundle mainBundle]])
	{
		task = [theTask retain];
		effortCount = [[task efforts] count];
		
		effortCell = [[[CellFactory cellFactory] createButtonCell] retain];
		[effortCell.button setTitleColor:[UIColor blackColor] forState:UIControlStateNormal];
		[effortCell setTarget:self action:@selector(onTrack:)];
	}

	return self;
}

- (void)viewDidLoad
{
	[super viewDidLoad];

	[self updateTrackButton];
	[self updateEffortTotal];
}

- (void)viewDidUnload
{
}

- (void)dealloc
{
	[self viewDidUnload];

	[effortCell release];
	[super dealloc];
}

- (void)onTrackedTasksCount:(NSDictionary *)dict
{
	trackedTasksCount = [[dict objectForKey:@"total"] intValue];
}

- (void)onTrack:(ButtonCell *)cell
{
	if ([task currentEffort])
	{
		[task stopTracking];
		[self updateTrackButton];
		[self.tableView reloadRowsAtIndexPaths:[NSArray arrayWithObject:[NSIndexPath indexPathForRow:0 inSection:1]] withRowAnimation:UITableViewRowAnimationFade];
	}
	else
	{
		Statement *st = [[Database connection] statementWithSQL:@"SELECT COUNT(*) AS total FROM CurrentEffort WHERE ended IS NULL"];
		trackedTasksCount = 0;
		[st execWithTarget:self action:@selector(onTrackedTasksCount:)];

		if (trackedTasksCount)
		{
			UIAlertView *alert = [[UIAlertView alloc] initWithTitle:_("Warning") message:[NSString stringWithFormat:_("There are %d task(s) currently tracked. Stop tracking them ?"), trackedTasksCount]
														   delegate:self cancelButtonTitle:_("Cancel") otherButtonTitles:_("Yes"), _("No"), nil];
			[alert show];
			[alert release];
		}
		else
		{
			[task startTracking];
			effortCount = [[task efforts] count];
			[self.tableView insertRowsAtIndexPaths:[NSArray arrayWithObject:[NSIndexPath indexPathForRow:0 inSection:1]] withRowAnimation:UITableViewRowAnimationRight];
			[self updateTrackButton];
		}
	}
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)toInterfaceOrientation
{
	return YES;
}

- (void)updateTrackButton
{
	BOOL isTracking = [task currentEffort] != nil;
	
	UIImage *img;
	
	if (isTracking)
	{
		img = [[UIImage imageNamed:@"blueButton.png"] stretchableImageWithLeftCapWidth:12.0 topCapHeight:0.0];
	}
	else
	{
		img = [[UIImage imageNamed:@"redButton.png"] stretchableImageWithLeftCapWidth:12.0 topCapHeight:0.0];
	}
	
	[effortCell.button setBackgroundImage:img forState:UIControlStateNormal];
	
	img = [[UIImage imageNamed:@"whiteButton.png"] stretchableImageWithLeftCapWidth:12.0 topCapHeight:0.0];
	[effortCell.button setBackgroundImage:img forState:UIControlStateHighlighted];
	
	if (isTracking)
		[effortCell.button setTitle:_("Stop tracking") forState:UIControlStateNormal];
	else
		[effortCell.button setTitle:_("Start tracking") forState:UIControlStateNormal];

	effortCount = [[task efforts] count];
	[self.tableView reloadSections:[NSIndexSet indexSetWithIndex:0] withRowAnimation:UITableViewRowAnimationNone];
}

- (void)onEffortTotal:(NSDictionary *)dict
{
	effortTotal += [[[TimeUtils instance] dateFromString:[dict objectForKey:@"ended"]] timeIntervalSinceDate:[[TimeUtils instance] dateFromString:[dict objectForKey:@"started"]]];
}

- (void)updateEffortTotal
{
	effortTotal = 0;
	[[[Database connection] statementWithSQL:[NSString stringWithFormat:@"SELECT started, ended FROM CurrentEffort WHERE ended IS NOT NULL AND taskId=%d", task.objectId]] execWithTarget:self action:@selector(onEffortTotal:)];
	[self.tableView reloadSections:[NSIndexSet indexSetWithIndex:1] withRowAnimation:UITableViewRowAnimationNone];
}

#pragma mark UIAlertViewDelegate methods

- (void)alertView:(UIAlertView *)alertView didDismissWithButtonIndex:(NSInteger)buttonIndex
{
	switch (buttonIndex)
	{
		case 0: // Cancel
			break;
		case 1: // Yes: stop tracking other tasks
		{
			NSString *now = [[TimeUtils instance] stringFromDate:[NSDate date]];
			Statement *req;
			if ([[Database connection] currentFile])
			{
				req = [[Database connection] statementWithSQL:@"UPDATE Effort SET ended=? WHERE ended IS NULL AND (fileId=? OR fileId IS NULL)"];
				[req bindInteger:[[[Database connection] currentFile] intValue] atIndex:2];
			}
			else
			{
				req = [[Database connection] statementWithSQL:@"UPDATE Effort SET ended=? WHERE ended IS NULL AND fileId IS NULL"];
			}
			[req bindString:now atIndex:1];
			[req exec];
		}
			// No break; intended
		case 2: // No, don't stop tracking others
			[task startTracking];
			effortCount = [[task efforts] count];
			[self.tableView insertRowsAtIndexPaths:[NSArray arrayWithObject:[NSIndexPath indexPathForRow:0 inSection:1]] withRowAnimation:UITableViewRowAnimationRight];
			[self updateTrackButton];
			break;
	}
}

#pragma mark Table view methods

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView
{
    return 2;
}

- (NSString *)tableView:(UITableView *)tableView titleForHeaderInSection:(NSInteger)section
{
	switch (section)
	{
		case 0:
		{
			if (effortCount)
				return [NSString stringWithFormat:_("%d effort(s)"), effortCount];
			else
				return _("No effort.");
		}
		case 1:
		{
			return [NSString formatTimeInterval:effortTotal];
		}
	}

	return nil;
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section
{
	switch (section)
	{
		case 0:
			return 1;
		case 1:
			return effortCount;
		default:
			break;
	}

	return 0;
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath
{
    if (indexPath.section == 0)
	{
		return effortCell;
	}
	else
	{
		static NSString *CellIdentifier = @"Cell";
		
		UITableViewCell *cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
		if (cell == nil)
		{
			cell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:CellIdentifier] autorelease];
		}
		
		Effort *effort = [[task efforts] objectAtIndex:indexPath.row];
		
		if (effort.ended)
		{
			NSTimeInterval duration = [effort.ended timeIntervalSinceDate:effort.started];
			cell.textLabel.text = [NSString formatTimeInterval:(NSInteger)duration];
		}
		else
		{
			NSString *s = [[DateUtils instance] stringFromDate:effort.started];
			cell.textLabel.text = [NSString stringWithFormat:_("Started %@"), s];
		}
		
		cell.selectionStyle = UITableViewCellSelectionStyleNone;
		
		return cell;
	}
}

@end

