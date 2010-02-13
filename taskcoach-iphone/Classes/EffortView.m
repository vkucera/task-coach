//
//  EffortView.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 30/01/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "EffortView.h"
#import "Task.h"
#import "Effort.h"
#import "DateUtils.h"
#import "String+Utils.h"
#import "i18n.h"

@implementation EffortView

- initWithTask:(Task *)theTask
{
	if (self = [super initWithNibName:@"EffortView" bundle:[NSBundle mainBundle]])
	{
		task = [theTask retain];
		efforts = [[task efforts] retain];
	}
	
	return self;
}

- (void)dealloc
{
	[task release];
	[efforts release];
	
	[super dealloc];
}

- (NSString *)formatTimeInterval:(NSInteger)interval
{
	NSMutableArray *components = [[[NSMutableArray alloc] init] autorelease];

	if (interval % 60)
	{
		[components insertObject:[NSString stringWithFormat:_("%d seconds"), interval % 60] atIndex:0];
	}

	interval /= 60;

	if (interval % 60)
	{
		[components insertObject:[NSString stringWithFormat:_("%d minutes"), interval % 60] atIndex:0];
	}

	interval /= 60;
	
	if (interval % 24)
	{
		[components insertObject:[NSString stringWithFormat:_("%d hours"), interval % 24] atIndex:0];
	}
	
	interval /= 24;
	if (interval)
	{
		[components insertObject:[NSString stringWithFormat:_("%d days"), interval] atIndex:0];
	}

	return [@", " stringByJoiningStrings:components];
}

#pragma mark Table view methods

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView
{
    return 1;
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section
{
	return [efforts count];
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath
{
    static NSString *CellIdentifier = @"Cell";
    
    UITableViewCell *cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];

    if (cell == nil)
	{
        cell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:CellIdentifier] autorelease];
    }

	Effort *effort = [efforts objectAtIndex:indexPath.row];

	if (effort.ended)
	{
		NSTimeInterval duration = [effort.ended timeIntervalSinceDate:effort.started];
		cell.textLabel.text = [self formatTimeInterval:(NSInteger)duration];
	}
	else
	{
		NSString *s = [[DateUtils instance] stringFromDate:effort.started];
		cell.textLabel.text = [NSString stringWithFormat:_("Started %@"), s];
	}

    return cell;
}

- (NSString *)tableView:(UITableView *)tableView titleForHeaderInSection:(NSInteger)section
{
	NSInteger total = 0;
	for (Effort *e in efforts)
		if (e.ended)
			total += [e.ended timeIntervalSinceDate:e.started];
		else
			total += [[NSDate date] timeIntervalSinceDate:e.started];
	return [NSString stringWithFormat:@"Total: %@", [self formatTimeInterval:total]];
}

@end

