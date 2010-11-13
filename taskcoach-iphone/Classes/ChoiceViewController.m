//
//  ChoiceViewController.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 13/11/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "ChoiceViewController.h"


@implementation ChoiceViewController

#pragma mark -
#pragma mark View lifecycle

- initWithChoices:(NSArray *)theChoices current:(NSInteger)current target:(id)theTarget action:(SEL)theAction
{
	if ((self = [super initWithNibName:@"ChoiceViewController" bundle:[NSBundle mainBundle]]))
	{
		choices = [theChoices retain];
		selection = current;
		target = theTarget;
		action = theAction;
	}

	return self;
}

- (void)dealloc
{
	[choices release];

    [super dealloc];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
	return YES;
}


#pragma mark -
#pragma mark Table view data source

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView
{
	return 1;
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section
{
	return [choices count];
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath
{
    static NSString *CellIdentifier = @"Cell";
    
    UITableViewCell *cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
    if (cell == nil)
	{
        cell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:CellIdentifier] autorelease];
    }

	cell.textLabel.text = [choices objectAtIndex:indexPath.row];
	cell.accessoryType = (indexPath.row == selection) ? UITableViewCellAccessoryCheckmark : UITableViewCellAccessoryNone;

    return cell;
}

#pragma mark -
#pragma mark Table view delegate

- (void)tableView:(UITableView *)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath
{
	[target performSelector:action withObject:[NSNumber numberWithInt:indexPath.row]];
}

@end

