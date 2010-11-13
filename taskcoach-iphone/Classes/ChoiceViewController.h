//
//  ChoiceViewController.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 13/11/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import <UIKit/UIKit.h>


@interface ChoiceViewController : UITableViewController
{
	id target;
	SEL action;
	NSArray *choices;
	NSInteger selection;
}

- initWithChoices:(NSArray *)choices current:(NSInteger)current target:(id)target action:(SEL)action;

@end
