//
//  TaskCelliPad.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 19/06/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import <Foundation/Foundation.h>

@class CDTask;
@class CheckView;

@interface TaskCelliPad : UITableViewCell
{
	UIImage *bgImage;

	CDTask *task;

	id target;
	SEL action;

	UILabel *subject;
	UILabel *priority;
	UILabel *infos;
	UITextView *description;
	UIImageView *tracking;
	CheckView *check;
}

@property (nonatomic, retain) CDTask *task;

@property (nonatomic, retain) IBOutlet UILabel *subject;
@property (nonatomic, retain) IBOutlet UILabel *priority;
@property (nonatomic, retain) IBOutlet UILabel *infos;
@property (nonatomic, retain) IBOutlet UITextView *description;
@property (nonatomic, retain) IBOutlet UIImageView *tracking;
@property (nonatomic, retain) IBOutlet CheckView *check;

- (void)setTask:(CDTask *)task target:(id)theTarget action:(SEL)theAction;

@end
